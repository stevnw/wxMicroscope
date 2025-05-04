"""
This is a program made specifically for the cheap USB microscopes (e.g. Jiusion B06WD843ZM), made by stevnw (https://github.com/stevnw)
I plan to add some more features at some point...

"""
import cv2
import wx
import threading
import os
import re

class WebcamPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent  # Store reference to parent frame
        self.mouse_pos = (0, 0)  # Initialize mouse position

        # Should open the camera - if not cycle through the /dev/videoX - e.g. ls /dev/video* -> should return something like /dev/video0... might be an idea to add a settings window at some point**
        self.capture = cv2.VideoCapture(0)  # or '/dev/video0' instead of 0
        if not self.capture.isOpened():
            print("Error: Could not open webcam.") # just in case really
            self.capture = None
            return

        # Timer for periodic frame updates
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_frame, self.timer)
        self.timer.Start(30)  # Refresh every 30 ms (~33 FPS)

        self.bitmap = wx.StaticBitmap(self) # to show the feed
        
        # Bind mouse movement event to track coordinates
        self.bitmap.Bind(wx.EVT_MOTION, self.on_mouse_move)

        # button stuff
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.top_panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.snapshot_button = wx.Button(self.top_panel, label="Capture")
        self.snapshot_button.Bind(wx.EVT_BUTTON, self.on_snapshot_button)

        top_sizer.Add(self.snapshot_button, 0, wx.ALL | wx.CENTER, 5)
        self.top_panel.SetSizer(top_sizer)

        # top panel thingy with a spacer - this is where the controls go lol
        self.sizer.Add(self.top_panel, 0, wx.EXPAND | wx.TOP, 10)  # 10px space at the top
        self.sizer.Add(self.bitmap, 1, wx.EXPAND)

        self.SetSizer(self.sizer)

        # capture stuff
        self._capturing = True
        self._thread = threading.Thread(target=self.capture_frames)
        self._thread.start()

        self.snapshot_counter = self.get_next_snapshot_number() # set counter based on existing images

    def on_mouse_move(self, event):
        self.mouse_pos = event.GetPosition() # Get mouse position relative to the bitmap
        
        # mouse coord & status bar stuff
        version_text = "Version: 0.1.2a"
        coords_text = f"X: {self.mouse_pos[0]} Y: {self.mouse_pos[1]}"
        status_text = f"{version_text} | {coords_text}"
        
        self.parent.SetStatusText(status_text)
        
        event.Skip()

    def capture_frames(self):
        while self._capturing:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame = frame

    def update_frame(self, event):
        if hasattr(self, 'frame'):
            frame = self.frame
            h, w = frame.shape[:2]
            image = wx.Bitmap.FromBuffer(w, h, frame)

            wx.CallAfter(self.bitmap.SetBitmap, image)
            wx.CallAfter(self.Layout)

    def release(self):
        self._capturing = False
        self._thread.join()
        if self.capture:
            self.capture.release()

    def get_next_snapshot_number(self):
        snapshot_files = [f for f in os.listdir() if re.match(r'snapshot-(\d{6})\.png', f)]
        if snapshot_files:
            numbers = [int(re.search(r'(\d{6})', f).group(1)) for f in snapshot_files]
            return max(numbers) + 1
        else:
            return 1  # Starts at 1, provided no snapshots exist

    def on_snapshot_button(self, event):
        if hasattr(self, 'frame'):
            frame = self.frame # Ccnvert the current frame to a format for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # needed to convert from RGB (wxPython) to BGR (OpenCV)
            
            snapshot_filename = f"snapshot-{self.snapshot_counter:06d}.png" # filename based on the snapshot counter
              
            cv2.imwrite(snapshot_filename, frame_bgr) # Save the snapshot

            dlg = wx.MessageDialog(self, f"Snapshot saved as {snapshot_filename}", "Snapshot", wx.OK | wx.ICON_INFORMATION) # confirmation dialog
            dlg.ShowModal()
            dlg.Destroy()

            self.snapshot_counter += 1  # step increase

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxMicroScope", size=(640, 620))

        self.cam_panel = WebcamPanel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.CreateStatusBar()

    def on_close(self, event):
        if self.cam_panel:
            self.cam_panel.release()
        self.Destroy()

# Start the app
app = wx.App(False)
frame = MainFrame()
frame.Show()
app.MainLoop()
