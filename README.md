# wxMicroscope
A wxpython based gui for USB digital microscopes (e.g. Jiusion B06WD843ZM)

Dependencies:

<pre>  pip install wxpython opencv-python </pre>

![image](https://github.com/user-attachments/assets/3893ca3f-d2c7-4558-8a28-9a350cc0cf92)
Version 0.1.2a - annotation and pixel measurement system

![snapshot-000004](https://github.com/user-attachments/assets/99fdd816-b9cf-4cbd-8ec6-d48b4462da5e)
Captured image, with annotations


To Do:
- [ ] Add a toggleable scale overlay
- [ ] Add a pointer marking, and distance measuring system
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
