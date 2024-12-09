import colorsys

import cv2
import numpy as np

RECT_SIZE = 100
H_SENSITIVITY = 30
S_H = 255
V_H = 255
S_L = 50
V_L = 50

HUE_GREEN = 60
HUE_BLUE = 120
HUE_RED = 180

S_SENSITIVITY = (S_H - S_L) / 2
V_SENSITIVITY = (V_H - V_L) / 2

V_VALUE = V_H - V_SENSITIVITY
S_VALUE = S_H - S_SENSITIVITY

BGR_GREEN = [0, 255, 0]
BGR_BLUE = [255, 0, 0]
BGR_RED = [0, 0, 255]

THICKNESS = 2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=720,
    display_height=480,
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


class Rectangle:
    def __init__(self, x, y, w, h, color=BGR_RED, h_sensitivity=H_SENSITIVITY,
                 s_value=S_VALUE, v_value=V_VALUE,
                 s_sensitivity=S_SENSITIVITY, v_sensitivity=V_SENSITIVITY,
                 name="red"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.color = color
        self.h_sensitivity = h_sensitivity
        self.s_value = s_value
        self.v_value = v_value
        self.s_sensitivity = s_sensitivity
        self.v_sensitivity = v_sensitivity
        self.rect = None
        self.is_checked = False

    @property
    def start_point(self):
        return self.x, self.y

    @property
    def end_point(self):
        return self.x + self.w, self.y + self.h

    def draw(self, frame):
        if self.is_checked:
            rect = cv2.rectangle(frame, self.start_point, self.end_point, self.color, thickness=cv2.FILLED)
        else:
            rect = cv2.rectangle(frame, self.start_point, self.end_point, self.color, THICKNESS)
        self.rect = rect
        return rect

    def write_text(self, color_rate):
        text_coord = (self.x, self.y + self.h + 40)
        if self.is_checked:
            return cv2.putText(self.rect, f" {self.name} ",
                               text_coord, FONT, FONT_SCALE, self.color, THICKNESS, cv2.LINE_AA)

        return cv2.putText(self.rect, f" not {self.name} ",
                           text_coord, FONT, FONT_SCALE, self.color, THICKNESS, cv2.LINE_AA)

    def color_rate(self, hsv_frame):
        hue = colorsys.rgb_to_hsv(self.color[2], self.color[1], self.color[0])
        upper = int(hue[0] * 180) + self.h_sensitivity
        lower = int(hue[0] * 180) - self.h_sensitivity
        if lower < 0:
            lower = lower % 180
            upper = lower + 2 * H_SENSITIVITY

        color_upper = np.array([upper, self.s_value + self.s_sensitivity, self.v_value + self.v_sensitivity])
        color_lower = np.array([lower, self.s_value - self.s_sensitivity, self.v_value - self.v_sensitivity])

        mask_frame = hsv_frame[self.start_point[1]:self.end_point[1] + 1, self.start_point[0]:self.end_point[0] + 1]
        mask_color = cv2.inRange(mask_frame, color_lower, color_upper)

        color_rate = np.count_nonzero(mask_color) / (self.w * self.h)
        self.check_color_rate(color_rate)

        return color_rate

    def check_color_rate(self, color_rate):
        self.is_checked = color_rate > 0.9 or self.is_checked


def process(rect_list, frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    check = True
    for rect in rect_list:
        rect.draw(frame)
        color_rate = rect.color_rate(hsv_frame)
        if not rect.is_checked:
            check = False
        rect.write_text(color_rate)
    if check:
        exit(0)
    return frame


if __name__ == '__main__':
    print('Press 4 to Quit the Application\n')

    rect_list = [
        Rectangle(400, 100, 100, 100),
        Rectangle(500, 100, 100, 100, color=BGR_BLUE, name="blue"),
        Rectangle(600, 100, 100, 100, color=BGR_GREEN, name="green"),
        Rectangle(700, 100, 100, 100)
    ]

    cap = cv2.VideoCapture(0) #gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)

    while (cap.isOpened()):
        # Take each Frame
        ret, frame = cap.read()
        # Flip Video vertically (180 Degrees)
        frame = cv2.flip(frame, 180)

        # Show video
        cv2.imshow('Cam', process(rect_list, frame))

        # Exit if "ESC" is pressed
        k = cv2.waitKey(30) & 0xFF
        if k == 27:  # ord 4
            # Quit
            print('Good Bye!')
            break
