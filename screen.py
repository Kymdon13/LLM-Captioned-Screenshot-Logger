import cv2
import mss
import requests
import json
import base64
import numpy as np


class ScreenCapture:
    def __init__(self, scale_factor=1, color=None):
        self.scale_factor = scale_factor
        self.color = color
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[0]
        frame = np.array(self.sct.grab(self.monitor))
        self.row, self.col, channel = frame.shape

    def capture_screen(self):
        sct_img = self.sct.grab(self.monitor)
        if sct_img is None:
            print("Failed to capture screen.")
            raise RuntimeError("Failed to capture screen.")

        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        if self.color is not None:
            frame = cv2.cvtColor(frame, self.color)

        return cv2.resize(
            frame,
            (self.col // self.scale_factor, self.row // self.scale_factor),
            cv2.INTER_AREA,
        )

    def release(self):
        self.sct.close()


if __name__ == "__main__":
    sc = ScreenCapture(scale_factor=2)
    frame = sc.capture_screen()
    cv2.imshow("Captured Frame", frame)
    if cv2.waitKey(0) & 0xFF == ord("q"):
        sc.release()
    cv2.destroyAllWindows()
