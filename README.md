# Crowd Speed Analysis
Estimating Pedestrian Speed using GPS Tracks

<p align="center">
  <img src="/images/Geo.JPG", width="500"/>  
</p>

How to reproduce:
----------------
<ol>
<li>Download or clone the repo</li>
<li>Move "testarea" vector data to the appropriate directory</li>
<li>In the script "PedestrianSpeed.py", change Paths variables to you directories</li>
<li>Copy the script into QGis python editor</li>
<li>One-click execution</li>
</ol>

The executed operations are:
----------------
<ol>
<li>  Clipping data based on "testarea"</li>
<li>  Adding Average speed field and values </li>
<li>  Adding Instant speed field and values </li>
<li>  Adding Flow direction field and values </li>
<li>  Boxplot for average speed of the tracks</li>
<li>  3D plot for the track
</ol>


<h2>Results</h2>
<p align="center">
  <img src="/images/figure_1.png", width="350"/>  
  <img src="/images/figure_2.jpeg", width="400"/>  
</p>

Tip: Expand the plot to fullscreen for better viewing

This project was developed by :
<ul>
  <li>Aws Dib</li>
  <li>Monica MAGAN</li>
  <li>Zhihao LIU</li>
  <li>Leon Yan-Feng GAW</li>
</ul>
