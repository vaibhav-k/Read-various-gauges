import cv2
import numpy as np
import requests

# Step 1: Install Dependencies (if not already installed)
# pip install opencv-python
# pip install requests

# Step 2: Capture or Load Images/Videos
# 0 stands for the default camera and can be changed later on
cap = cv2.VideoCapture(0)
# Load pre-recorded video
# cap = cv2.VideoCapture('path/to/video.mp4')


def preprocess_frame(frame):
    """
    Preprocesses a frame.

    Args:
        frame (numpy.ndarray): The input frame.

    Returns:
        numpy.ndarray: The preprocessed frame.
    """
    resized_frame = cv2.resize(frame, (640, 480))
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
    return binary_frame


def detect_gauge(frame):
    """
    Detects and localizes a gauge in the frame.

    Args:
        frame (numpy.ndarray): The input frame.

    Returns:
        Tuple[int, int, int, int]: The coordinates (x, y) and dimensions (width, height) of the detected gauge.
    """
    template = cv2.imread("path/to/template.jpg", 0)
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    gauge_x, gauge_y = max_loc
    gauge_w, gauge_h = template.shape[::-1]
    return gauge_x, gauge_y, gauge_w, gauge_h


def extract_reading(frame, x, y, w, h):
    """
    Extracts the reading from the gauge region in the frame.

    Args:
        frame (numpy.ndarray): The input frame.
        x (int): The x-coordinate of the gauge region.
        y (int): The y-coordinate of the gauge region.
        w (int): The width of the gauge region.
        h (int): The height of the gauge region.
    """
    roi = frame[y: y + h, x: x + w]
    _, contours, _ = cv2.findContours(
        roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                centroid_x = int(M["m10"] / M["m00"])
                centroid_y = int(M["m01"] / M["m00"])
        else:
            print("Skipping contour with area less than or equal to 100")


def convert_reading(reading):
    """
    Converts the reading if needed.

    Args:
        reading: The input reading.

    Returns:
        The converted reading.
    """
    converted_reading = reading * 2
    return converted_reading


def send_reading(reading):
    """
    Sends the reading to a central dashboard or API.

    Args:
        reading: The reading to be sent.
    """
    payload = {"reading": reading}
    response = requests.post("http://your-dashboard-url", data=payload)
    if response.status_code == 200:
        print("Reading sent successfully!")


while True:
    ret, frame = cap.read()

    processed_frame = preprocess_frame(frame)

    gauge_x, gauge_y, gauge_w, gauge_h = detect_gauge(processed_frame)

    reading = extract_reading(processed_frame, gauge_x,
                              gauge_y, gauge_w, gauge_h)

    converted_reading = convert_reading(reading)

    send_reading(converted_reading)

    cv2.rectangle(
        frame,
        (gauge_x, gauge_y),
        (gauge_x + gauge_w, gauge_y + gauge_h),
        (0, 255, 0),
        2,
    )
    cv2.imshow("Gauge Analysis", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
