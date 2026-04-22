import mss
import base64
import cv2
import numpy as np


def capture_screenshot_b64():
    """Capture the primary monitor and return a base64 JPEG + resolution."""
    with mss.mss() as sct:
        mon = sct.monitors[1]
        screenshot = sct.grab(mon)
        img_np = np.array(screenshot)

    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
    _, buffer = cv2.imencode(".jpg", img_bgr, encode_params)
    b64_str = base64.b64encode(buffer).decode("utf-8")

    height, width = img_bgr.shape[:2]
    return b64_str, width, height
