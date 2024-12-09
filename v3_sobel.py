# ITMO University
# Mobile Computer Vision course
# 2020
# by Aleksei Denisov
# denisov@itmo.ru

import cv2
import numpy as np

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def show_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=4))
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            ret_val, frame = cap.read()
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Denoise 
            gray = cv2.GaussianBlur(gray,(3,3),0)

            # Sobel filter
            h = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
            v = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
            #sobel = cv2.addWeighted(h, 0.5, v, 0.5, 0)
            der_arr = np.array([h,v])
            sobel = np.linalg.norm(der_arr, axis=0)
            thd_abs = cv2.convertScaleAbs(sobel, alpha=2)

            # Show video
            cv2.imshow('Detect Boundaries',thd_abs)
            # This also acts as
            keyCode = cv2.waitKey(1) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    show_camera()
