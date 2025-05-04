"""
This is a program made specifically for the cheap USB microscopes (e.g. Jiusion B06WD843ZM), made by stevnw (https://github.com/stevnw) - This is build 0.1.2a
You can capture images, annotate, calculate lengths (in px - plan to add calibrations and conversions to get real world values instead) and export these values
The code is becoming a bit messy, but it is functional :D

"""
import cv2
import wx
import threading
import os
import re
import numpy as np

CURSOR_OFFSET = wx.Point(-35, -22) # This is adjustments for my specific system - I don't think this is universal and as such its probably a stupid way to do it... it works though!

class WebcamPanel(wx.Panel): # This is the control panel buttons and logic
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mouse_pos = (0, 0)

        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Could not open webcam.")
            self.capture = None
            return

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_frame, self.timer)
        self.timer.Start(30)

        self.bitmap = wx.StaticBitmap(self)
        self.bitmap.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.bitmap.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.bitmap.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.bitmap.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.snapshot_button = wx.Button(self.top_panel, label="Capture")
        self.snapshot_button.Bind(wx.EVT_BUTTON, self.on_snapshot_button)

        self.annotation_button = wx.Button(self.top_panel, label="Annotate")
        self.annotation_button.Bind(wx.EVT_BUTTON, self.on_annotation_button)

        self.label_toggle_button = wx.ToggleButton(self.top_panel, label="Show Labels")
        self.label_toggle_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_label_toggle)
        self.show_labels = False

        self.measure_toggle_button = wx.ToggleButton(self.top_panel, label="Show Measurements")
        self.measure_toggle_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_measure_toggle)
        self.show_measurements = False

        self.export_button = wx.Button(self.top_panel, label="Export")
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export_button)

        top_sizer.Add(self.snapshot_button, 0, wx.ALL | wx.CENTER, 5)
        top_sizer.Add(self.annotation_button, 0, wx.ALL | wx.CENTER, 5)
        top_sizer.Add(self.label_toggle_button, 0, wx.ALL | wx.CENTER, 5)
        top_sizer.Add(self.measure_toggle_button, 0, wx.ALL | wx.CENTER, 5)
        top_sizer.Add(self.export_button, 0, wx.ALL | wx.CENTER, 5)
        self.top_panel.SetSizer(top_sizer)

        self.sizer.Add(self.top_panel, 0, wx.EXPAND | wx.TOP, 10)
        self.sizer.Add(self.bitmap, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self._capturing = True
        self._thread = threading.Thread(target=self.capture_frames)
        self._thread.start()

        self.snapshot_counter = self.get_next_snapshot_number()

        self.annotation_mode = False
        self.drawing = False
        self.line_start = None
        self.line_end = None
        self.annotation_color = (255, 0, 0)
        self.annotations = []

    def corrected_mouse_position(self, event): # This is to fix the offset - idk if its just for my machine (debian) though... Can probs make this into a user config calibration thingy later...
        pos = event.GetPosition()
        return (pos.x + CURSOR_OFFSET.x, pos.y + CURSOR_OFFSET.y)

    def on_mouse_move(self, event): # x, y pos of mouse
        corrected = self.corrected_mouse_position(event)
        self.mouse_pos = corrected

        version_text = "Version: 0.1.2a"
        coords_text = f"X: {corrected[0]} Y: {corrected[1]}"
        mode_text = "Annotation ON" if self.annotation_mode else ""
        status_text = f"{version_text} | {coords_text} | {mode_text}"
        self.parent.SetStatusText(status_text)

        if self.annotation_mode and self.drawing:
            self.line_end = corrected

        event.Skip()

    def on_mouse_down(self, event):
        if self.annotation_mode:
            self.drawing = True
            self.line_start = self.corrected_mouse_position(event)
            self.line_end = self.line_start
        event.Skip()

    def on_mouse_up(self, event):
        if self.annotation_mode and self.drawing:
            self.drawing = False
            self.line_end = self.corrected_mouse_position(event)
            if self.line_start and self.line_end and self.line_start != self.line_end:
                dx = self.line_end[0] - self.line_start[0]
                dy = self.line_end[1] - self.line_start[1]
                distance = int(np.hypot(dx, dy))
                label_id = f"L{len(self.annotations) + 1}"
                label_pos = (self.line_start[0], self.line_start[1] - 10)

                self.annotations.append({
                    'start': self.line_start,
                    'end': self.line_end,
                    'color': self.annotation_color,
                    'distance': distance,
                    'label': label_id,
                    'label_pos': label_pos
                })

                print(f"{label_id} drawn: {distance}px from {self.line_start} to {self.line_end}")
        event.Skip()

    def on_right_click(self, event): # This is to delete annotations...
        if not self.annotation_mode:
            return
        click_pos = self.corrected_mouse_position(event)
        for i, ann in enumerate(self.annotations):
            if self.is_near_line(click_pos, ann['start'], ann['end']):
                del self.annotations[i]
                print(f"Annotation removed at click near {click_pos}")
                break

    def is_near_line(self, point, start, end, threshold=8): # This is some leeway for the erasure of annotations 
        px, py = point
        x1, y1 = start
        x2, y2 = end
        if (x1, y1) == (x2, y2):
            return np.hypot(px - x1, py - y1) <= threshold
        else:
            num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
            den = np.hypot(y2 - y1, x2 - x1)
            return num / den <= threshold

    def on_annotation_button(self, event): # Annotation button logic - allows for the colour to be chosen using a colour wheel - should default to red, currently defaults to black... Problem for later
        self.annotation_mode = not self.annotation_mode
        if self.annotation_mode:
            dlg = wx.ColourDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                wx_color = dlg.GetColourData().GetColour()
                self.annotation_color = (wx_color.Red(), wx_color.Green(), wx_color.Blue())
            else:
                self.annotation_color = (255, 0, 0)
            dlg.Destroy()
            self.annotation_button.SetLabel("Stop Annotating")
            self.bitmap.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        else:
            self.annotation_button.SetLabel("Annotate")
            self.bitmap.SetCursor(wx.NullCursor)

    def on_label_toggle(self, event):
        self.show_labels = event.GetEventObject().GetValue()

    def on_measure_toggle(self, event):
        self.show_measurements = event.GetEventObject().GetValue()

    def on_export_button(self, event): 
		
		"""export to csv in format: label, length_px -> will allow for the conversion of px to irl values... A hard coded conversion will be inaccurate if
			other users use different USB microscopes with differnt focal lengths I am pretty sure - so this would be a stupid idea... I think the user should be able to 
			use something of known length value to calibrate their own thing - this will likely be a session by session config option?
		"""
        if not self.annotations:
            dlg = wx.MessageDialog(self, "No annotations to export.", "Export CSV", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        try:
            with open("annotations.csv", "w") as f:
                f.write("label,length_px\n")
                for ann in self.annotations:
                    f.write(f"{ann['label']},{ann['distance']}\n")

            dlg = wx.MessageDialog(self, "Annotations exported to annotations.csv", "Export CSV", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        except Exception as e:
            dlg = wx.MessageDialog(self, f"Failed to export CSV:\n{str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def capture_frames(self):
        while self._capturing:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame = frame.copy()

    def update_frame(self, event):
        if hasattr(self, 'frame'):
            display_frame = self.frame.copy()

            for ann in self.annotations:
                cv2.line(display_frame, ann['start'], ann['end'], ann['color'], 2)

                if self.show_labels:
                    cv2.putText(display_frame, ann['label'], ann['label_pos'],
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, ann['color'], 1, cv2.LINE_AA)

                if self.show_measurements:
                    dist_text = f"{ann['distance']} px"
                    dist_pos = (ann['label_pos'][0], ann['label_pos'][1] - 15)
                    cv2.putText(display_frame, dist_text, dist_pos,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, ann['color'], 1, cv2.LINE_AA)

            if self.annotation_mode and self.drawing and self.line_start and self.line_end:
                cv2.line(display_frame, self.line_start, self.line_end, self.annotation_color, 2)

            h, w = display_frame.shape[:2]
            image = wx.Bitmap.FromBuffer(w, h, display_frame)

            wx.CallAfter(self.bitmap.SetBitmap, image)
            wx.CallAfter(self.Layout)

    def release(self):
        self._capturing = False
        self._thread.join()
        if self.capture:
            self.capture.release()

    def get_next_snapshot_number(self): # Checks snapshot file names - honestly might swap to a YYYYMMDDHHMMSS format instead - as I should also do with the export csv names... JOB FOR LATER!
        snapshot_files = [f for f in os.listdir() if re.match(r'snapshot-(\d{6})\.png', f)]
        if snapshot_files:
            numbers = [int(re.search(r'(\d{6})', f).group(1)) for f in snapshot_files]
            return max(numbers) + 1
        else:
            return 1

    def on_snapshot_button(self, event):
        if hasattr(self, 'frame'):
            frame_with_annotations = self.frame.copy()

            for ann in self.annotations:
                cv2.line(frame_with_annotations, ann['start'], ann['end'], ann['color'], 2)
                if self.show_labels:
                    cv2.putText(frame_with_annotations, ann['label'], ann['label_pos'],
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, ann['color'], 1, cv2.LINE_AA)
                if self.show_measurements:
                    dist_text = f"{ann['distance']} px"
                    dist_pos = (ann['label_pos'][0], ann['label_pos'][1] - 15)
                    cv2.putText(frame_with_annotations, dist_text, dist_pos,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, ann['color'], 1, cv2.LINE_AA)

            frame_bgr = cv2.cvtColor(frame_with_annotations, cv2.COLOR_RGB2BGR)
            snapshot_filename = f"snapshot-{self.snapshot_counter:06d}.png"

            cv2.imwrite(snapshot_filename, frame_bgr)

            dlg = wx.MessageDialog(self, f"Snapshot saved as {snapshot_filename}", "Snapshot", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

            self.snapshot_counter += 1

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxMicroScope", size=(720, 640))
        self.cam_panel = WebcamPanel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.CreateStatusBar()

    def on_close(self, event):
        if self.cam_panel:
            self.cam_panel.release()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Center()
    frame.Show()
    app.MainLoop()
