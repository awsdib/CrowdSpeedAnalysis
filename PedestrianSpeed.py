import os,ogr
from datetime import datetime, date, time
import math, csv

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D

import processing



baseDir = "E:\\_SOSE2017\\PIG\\4project\\"

srcVectors = baseDir + "old\\EoT Data\\smartphone_data\\"

outVectorsPath = baseDir + 'newclip\\clippedData\\'

clipPolygon = baseDir + "newclip\\testarea2\\testarea2.shp"




shppath1 = "tp1_17-17-11_nach-abpfiff.shp"
shppath2 = "tp1_17-17-29_nach-abpfiff.shp"
shppath3 =  "tp2_17-17-27_nach-abpfiff.shp"


vectorFilesList = [shppath1, shppath2, shppath3]


print 'Clipping tracks started'
for shapefile in vectorFilesList :
  processing.runalg("qgis:clip", srcVectors+shapefile, clipPolygon, outVectorsPath+shapefile)
  print 'file ', shapefile , ' is clipped and saved to: ', outVectorsPath+shapefile

print 'Clipping tracks finished'
print '-----------------------------------------'


vectorFilesList = [outVectorsPath+shppath1, outVectorsPath+ shppath2, outVectorsPath+shppath3]

driver = ogr.GetDriverByName('ESRI Shapefile')


#  Definition for helper variables
i = 0
velVector = []

prevPoint = []
currentPoint = []

stream_flow =[]
response_flow =[]


def fieldExists(layerDefinition, fieldName):
    """
    Helper function to compare lists
    returns boolean result
    """
    field_names = [layerDefinition.GetFieldDefn(i).GetName() for i in range(layerDefinition.GetFieldCount()) ]
    return ( len(filter(lambda x: fieldName in x, field_names)) <> 0)

def createField(selected_layer, newFieldName, newFieldType):
    """
    Helper function to compare lists
    returns boolean result
    """
    field = ogr.FieldDefn(newFieldName, newFieldType)
    selected_layer.CreateField(field)

def is_equal(p1,p2):
    """
    Helper function for compare lists
    returns boolean result
    """
    return set(p1)==set(p2)

def dms2dd(degrees, minutes, seconds):
    """
      Converts angles in degrees, minutes and seconds into decimal degrees format    
    """
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    return dd;

def dd2dms(dd):
    """
      Converts angles in decimal degrees into degrees, minutes and seconds format
    """
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return deg,mnt,sec

def points2distance(start,  end):
  """
    Calculate distance (in kilometers) between two points given as (long, latt) pairs
  """
  start_long = math.radians(recalculate_coordinate(start[0],  'deg'))
  #print 'dzcx ',start_long
  start_latt = math.radians(recalculate_coordinate(start[1],  'deg'))

  end_long = math.radians(recalculate_coordinate(end[0],  'deg'))
  end_latt = math.radians(recalculate_coordinate(end[1],  'deg'))
  
  d_latt = end_latt - start_latt
  d_long = end_long - start_long
  
  r = 6371
  hav = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
  c = 2 * r * math.asin(math.sqrt(hav))
  return c

def recalculate_coordinate(val,  _as=None):
  """
    Accepts a coordinate as a tuple (degree, minutes, seconds)
    You can give only one of them (e.g. only minutes as a floating point number) and it will be duly
    recalculated into degrees, minutes and seconds.
    Return value can be specified as 'deg', 'min' or 'sec'; default return value is a proper coordinate tuple.
  """
  deg,  min,  sec = val
  # pass outstanding values from right to left
  min = (min or 0) + int(sec) / 60
  sec = sec % 60
  deg = (deg or 0) + int(min) / 60
  min = min % 60
  # pass decimal part from left to right
  dfrac,  dint = math.modf(deg)
  min = min + dfrac * 60
  deg = dint
  mfrac,  mint = math.modf(min)
  sec = sec + mfrac * 60
  min = mint
  if _as:
    sec = sec + min * 60 + deg * 3600
    if _as == 'sec': return sec
    if _as == 'min': return sec / 60
    if _as == 'deg': return sec / 3600
  return deg,  min,  sec

def GetSpeed( p1, p2 , delta ):

    start_lat_dd = float(p1[0])
    start_lon_dd = float(p1[1])

    start_lat_dms = dd2dms(start_lat_dd)
    start_lon_dms = dd2dms(start_lon_dd)


    end_lat_dd = float(p2[0])
    end_lon_dd = float(p2[1])

    end_lat_dms = dd2dms(end_lat_dd)
    end_lon_dms = dd2dms(end_lon_dd)


    start = [start_lat_dms,start_lon_dms]
    end = [end_lat_dms,end_lon_dms]


    distance = points2distance(start,end)

    speed = distance*1000/delta.seconds

    return speed




for shapefile in vectorFilesList :
    print "Processing file: ", shapefile
    # Opening the datasource
    datasource = driver.Open(shapefile,1)

    # Getting the layer
    layer = datasource.GetLayer(0)
    layerDefinition = layer.GetLayerDefn()
    

    # Creating the required fields if they don't exist
    if( fieldExists(layerDefinition, 'avgVel') == False ):
        createField(layer, 'avgVel', ogr.OFTReal)
        print "New field (avgVel) is added to the table"

    if( fieldExists(layerDefinition, 'instVel') == False ):
        createField(layer, 'instVel', ogr.OFTReal)
        print "New field (instVel) is added to the table"
        
    if( fieldExists(layerDefinition, 'flow') == False ):
        createField(layer, 'flow', ogr.OFTInteger)
        print "New field (flow) is added to the table"
        
    i = 0
    for feat in layer:
        
        """
          01- Region: Average velocity
        """
        # extracting location and time feature values 
        lat = feat.GetField('lat')
        lon = feat.GetField('lon')
        ts = feat.GetField('date')
        currentPoint = [lat,lon,ts]

        # condition to handle  the first iteration where no previous point exists
        if( len(prevPoint) > 2):
            time1 = prevPoint[2]
            time2 = currentPoint[2]

            # converting to object
            time1 = datetime.strptime(time1, '%Y-%m-%d_%H-%M-%S')
            time2 = datetime.strptime(time2, '%Y-%m-%d_%H-%M-%S')

            # time difference
            delta = time2-time1

            # distance functions are called from inside this function
            speed = GetSpeed( prevPoint , currentPoint , delta)

            feat.SetField('avgVel',speed)
            layer.SetFeature(feat)
            
            #velVector.append(speed)
        prevPoint = currentPoint

        i+=1
    print "Avarage velocity is calculated for ",i, " points."
    #print velVector

    """
    02- Region: Instant velocity
    """
    i=0
    feat = layer.GetFeature(0)
    prevPoint = []
    currentPoint = []
    while(feat):
      feat = layer.GetFeature(i)
      if (feat is None):
          break
      #print '--',i
      prevPoint = currentPoint
      currentPoint = [feat.GetField('lat'),feat.GetField('lon')]  

      occurence=0
      if(is_equal(currentPoint,prevPoint)):
        while(is_equal(currentPoint,prevPoint)):
          occurence+=1
          i+=1
          feat = layer.GetFeature(i)
          if( feat is None):
              break
          prevPoint = currentPoint
          currentPoint = [feat.GetField('lat'),feat.GetField('lon')]
        #print 'point : ', prevPoint[0],' ,occurence: ',occurence
        if( feat is None):
          break
        #print 'cur: ', feat.GetField('date')
        speed = feat.GetField('avgVel')
        velo = speed / occurence
        for j in range(i-occurence,i):
          feat = layer.GetFeature(j)
          #print feat.GetField('date')
          feat.SetField('instVel',velo)
          layer.SetFeature(feat)
      else:
        feat.SetField('instVel',feat.GetField('avgVel'))
        layer.SetFeature(feat)
        i+=1
    print 'Instant velocity for ', i,' points is added'

    """
    03- Region: Flow segmentation
    """
    out_flow = 0
    in_flow = 1


    maxlat = 0
    ch=0

    no_out=0
    no_in=0


    feat = layer.GetFeature(0)
    i=0

    while(feat):
        curlat = feat.GetField('lat')
        if(curlat >= maxlat):
            maxlat = curlat
            feat.SetField('flow',out_flow)
            no_out = no_out +1
        else:
            feat.SetField('flow',in_flow)
            no_in = no_in + 1

        layer.SetFeature(feat)
        
        if(feat.GetField('flow') == 0): 
            stream_flow .append( feat.GetField('instVel') )
        else:
            response_flow.append(feat.GetField('instVel'))

        i=i+1
        feat = layer.GetFeature(i)
        
      
    print 'Flow direction is set, out points: ',no_out,' , in points: ',no_in,' , of total: ',i-1,' , based on maximum latitude of: ',maxlat

    print "--------------------------------"

"""
 04- Region: Boxplot
"""

# Create a figure with 1x2 subplot and make the left subplot active
plt.subplot(1, 2, 1)

# Plot a boxplot of the speeds of stream flow
plt.boxplot((filter(None, stream_flow)))
plt.xlabel('Stream Flow')
plt.ylabel('Speed in meters per second')
plt.tick_params(axis = 'x',
                which = 'both',
                bottom = 'off',
                top = 'off',
                labelbottom = 'off')
plt.ylim(0, 5)

# Make the right subplot active in the current 1x2 subplot grid
plt.subplot(1, 2, 2)

# Plot a boxplot of the speeds of response flow
plt.boxplot((filter(None, response_flow)))
plt.xlabel('Response Flow')
plt.tick_params(axis = 'x',
                which = 'both',
                bottom = 'off',
                top = 'off',
                labelbottom = 'off')
plt.ylim(0, 5)

# Set title and show plot.
plt.suptitle('Speeds of Stream and Response Flows')
plt.show()

# Convert stream_flow from list to array and calculate median and standard dev.
sfarr =  np.asarray(filter(None, stream_flow))
print "For stream flow: "
print "-----------------"
print 'Median: ',np.median(sfarr)
print 'Standard Deviation: ',np.std(sfarr)

# Convert response_flow from list to array and calculate median and standard dev.
rfarr =  np.asarray(filter(None, response_flow))
print "For response flow: "
print "-----------------"
print 'Median: ',np.median(rfarr)
print 'Standard Deviation: ',np.std(rfarr)

print'The avarage median: ',(np.median(rfarr)/np.median(sfarr))*100.0

"""
 05- Region: 3D plot
"""

# Lists to hold the initial values of latitude, longitude and speed
lat = []
lon = []
speed = []
 
# Get the layer
datasource = driver.Open(outVectorsPath+shppath1,1)
layer = datasource.GetLayer(0)

for feat in layer:
    lat.append(feat.GetField('lat'))
    lon.append(feat.GetField('lon'))
    if(feat.GetField('instVel') is None):
        speed.append(0)
    else:
        speed.append(feat.GetField('instVel'))
del datasource

#list to hold the calculated values of the adjacent 10 points
speed_mean = []
lat_mean = []
lon_mean = []

#calculate the mean value of the adjacent 10 points
speed_mean = [sum(x) / float(len(x))
 for x in (speed[k : k + 10]
           for k in range(0, len(speed), 10))]
           
lat_mean = [sum(x) / float(len(x))
 for x in (lat[k : k + 10]
           for k in range(0, len(lat), 10))]           

lon_mean = [sum(x) / float(len(x))
 for x in (lon[k : k + 10]
           for k in range(0, len(lon), 10))]
           

#list to hold values along the stream
lat_mean_away = []
lon_mean_away = []
speed_mean_away = []

#list to hold values against the stream
lat_mean_back = []
lon_mean_back = []
speed_mean_back = []

#seperate the trail into two parts, along the stream and against the stream
for i in range(len(lon_mean)):
    if(i <= lat_mean.index(max(lat_mean))):
        lon_mean_away.append(lon_mean[i])
        lat_mean_away.append(lat_mean[i])
        speed_mean_away.append(speed_mean[i])
    else:
        lon_mean_back.append(lon_mean[i])
        lat_mean_back.append(lat_mean[i])
        speed_mean_back.append(speed_mean[i])


#final plot
mpl.rcParams['legend.fontsize'] = 15
fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot(lat_mean_away, lon_mean_away, speed_mean_away,"g-", label='Along Stream')
ax.plot(lat_mean_back, lon_mean_back, speed_mean_back,"r-", label='Against Stream')


#set legend, axes labels and title
ax.legend()
ax.set_xlabel('Latitude',fontsize=18)
ax.set_ylabel('Longitude',fontsize=18)
ax.set_zlabel('Speed',fontsize=18)
ax.set_title('Speed Curve in 3D View',fontsize=20)

#get rid of the axes values
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.set_zticklabels([])

plt.show()
