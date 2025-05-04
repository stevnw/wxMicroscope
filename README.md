# wxMicroscope
A wxpython based gui for USB digital microscopes (e.g. Jiusion B06WD843ZM)

Dependencies:

<pre>  pip install wxpython opencv-python </pre>


![image](https://github.com/user-attachments/assets/682885fb-a5d4-4d8f-83b9-3b5767a99a7d)

Version 0.1.2a - annotation and pixel measurement system


![snapshot-000005](https://github.com/user-attachments/assets/275dc017-8965-4d46-93e6-4211e0536a5c)

Captured image, with annotations

Exported data:
<pre>
label,length_px
L1,322
L2,72  
</pre>


To Do:
- [ ] Add a toggleable scale overlay
- [x] Add a pointer marking, and distance measuring system
- [ ] Filters (nothing stupid though)
- [ ] Settings (gui + config thingy??)

____

## For my own future reference

#### Camera Specs

<b>Product description:</b> 

- Focus Range: from 1mm to 250mm
- Frame Rate: Max 30f/s under 600 Lux Brightness
- Magnification Ratio: 40x to 1000x

<b>Real(er) specs:</b>

I think its much shittier than this - the 1000x magnification is a very comical claim. Its more of a focusing wheel than a zoom.

The resolution is 640x480 (I believe 0.3 Megapixel ?) - magnification is in practice is only around 40x - 50x (very generous rounding up)

I think I will need to triple check this, but my assumed maths is 40x the fov is ~ 11mm x 8mm with an actual magnification of ~15x ???



- this is generally the best I can get focused

![snapshot-000010](https://github.com/user-attachments/assets/057d7ee1-46bd-435e-9d6a-e0c04d46cbaf)
