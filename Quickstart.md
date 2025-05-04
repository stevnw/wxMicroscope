# wxMicroscope Quick Start Guide

## Dependencies issues

You will need the wxPython and opencv-python libraries to use this program.

<pre>  pip install wxpython opencv-python </pre>

To launch:

<pre> python wxMS.py </pre>

## Features

This is a comprehensive overview of the currently implemented features in version 0.1.2a of wxMS.py.

1. <b>Capture:</b>
    Click "Capture" to take picture. Any annotations made will be saved onto the image.

2. <b>Annotation:</b>

    Click the "Annotate" button and you can then pick a colour using the colour wheel:
   
   ![image](https://github.com/user-attachments/assets/f0008e33-5dad-4438-9a6a-2621c71d640b)

   After you choose a colour you can then left click to draw a line - where you click will be the point of origin.

   If you make a mistake during the annotation process, you can right click on a line, which will remove the individual line.

   Click "Show Labels" which will display L1, L2 etc in the same colour used for the annotation. The labels are in order of the added line.

   Click "Show Measurements" which will display the pixel length of the line.

   Click "Export" to obtain a .csv file of the measurements. This will look something like:

   <pre>
        label,length_px
        L1,322
        L2,72  
   </pre>

   
   
