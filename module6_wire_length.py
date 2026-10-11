#!/usr/bin/env python3
import cv2
import numpy as np
import os

CAMERA_INDEX = 2
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
VERSION = "v2"
IMAGES_DIR = f"images_{VERSION}"
os.makedirs(IMAGES_DIR, exist_ok=True)
CAPTURED_IMAGE_PATH = os.path.join(IMAGES_DIR, "captured_image.jpg")
COIN_DIAMETER_MM = 19.05

def phase1_camera_setup_and_capture():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Cannot open camera at index", CAMERA_INDEX)
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Camera opened. Requested:", CAPTURE_WIDTH, "x", CAPTURE_HEIGHT, "Actual:", actual_w, "x", actual_h)
    captured = None
    window_name = "Setup – Align Penny and Wire (live)"
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from camera")
            break
        display = frame.copy()
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            grayb = cv2.medianBlur(gray, 5)
            circles = cv2.HoughCircles(grayb, cv2.HOUGH_GRADIENT, 1.2, 50, param1=50, param2=30, minRadius=10, maxRadius=300)
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                x, y, r = circles[0]
                diam = 2 * r
                ppm = diam / COIN_DIAMETER_MM
                cv2.circle(display, (x, y), r, (0, 255, 0), 3)
                cv2.circle(display, (x, y), 2, (0, 0, 255), 3)
                cv2.putText(display, "PENNY", (x - 30, y - r - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower1 = np.array([0, 100, 50])
                upper1 = np.array([10, 255, 255])
                lower2 = np.array([160, 100, 50])
                upper2 = np.array([180, 255, 255])
                mask1 = cv2.inRange(hsv, lower1, upper1)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                red = cv2.bitwise_or(mask1, mask2)
                contours, _ = cv2.findContours(red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    raise Exception("no red")
                main = max(contours, key=cv2.contourArea)
                if cv2.contourArea(main) < 500:
                    raise Exception("small red")
                mask = np.zeros(red.shape, np.uint8)
                cv2.drawContours(mask, [main], -1, 255, -1)
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
                skel = np.zeros(mask.shape, np.uint8)
                element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                eroded = mask.copy()
                while True:
                    temp = cv2.erode(eroded, element)
                    temp2 = cv2.dilate(temp, element)
                    temp2 = cv2.subtract(eroded, temp2)
                    skel = cv2.bitwise_or(skel, temp2)
                    eroded = temp.copy()
                    if cv2.countNonZero(eroded) == 0:
                        break
                contours, _ = cv2.findContours(skel, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                length_px = 0.0
                if contours:
                    longest = max(contours, key=lambda c: cv2.arcLength(c, False), default=None)
                    if longest is not None:
                        length_px = cv2.arcLength(longest, False)
                length_mm = length_px / ppm if ppm > 0 else 0
                display[skel > 0] = (0, 255, 255)
                cv2.drawContours(display, [main], -1, (255, 0, 255), 5)
                x,y,w,h = cv2.boundingRect(main)
                cv2.rectangle(display, (x,y), (x+w, y+h), (0, 255, 255), 3)
                cv2.putText(display, "RED STRING", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                cv2.putText(display, "Penny diameter: 19.05 mm", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(display, "String length: " + str(round(length_mm, 2)) + " mm", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
                cv2.putText(display, "ppm: " + str(round(ppm, 2)), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
        except:
            pass
        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') or key == ord(' '):
            captured = frame.copy()
            cv2.imwrite(CAPTURED_IMAGE_PATH, captured)
            print("Image captured. Penny and red string should both be fully visible. Confirm before continuing?")
            break
        if key == ord('q') or key == ord('Q'):
            print("Quit requested (Q)")
            break
        if key == 27:
            print("Capture cancelled (ESC)")
            break
    cap.release()
    cv2.destroyAllWindows()
    if captured is not None:
        confirm_window = "Captured Preview – Review"
        cv2.imshow(confirm_window, captured)
        cv2.waitKey(200)
        response = input("Confirm capture and continue? (y/n): ").strip().lower()
        cv2.destroyAllWindows()
        if response != 'y':
            print("Not confirmed. Exiting Phase 1.")
            return None
        print("Capture confirmed. Proceeding.")
        return captured
    return None

def phase2_coin_detection_and_calibration(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=300)
    if circles is None:
        print("Error: No coin detected via Hough")
        return None
    circles = np.round(circles[0, :]).astype("int")
    if len(circles) == 0:
        print("Error: No coin circles after round")
        return None
    x, y, r = circles[0]
    diam_px = 2 * r
    if diam_px < 10:
        print("Error: Detected coin too small")
        return None
    pixels_per_mm = diam_px / COIN_DIAMETER_MM
    print("Penny diameter detected at", x, y, "radius", r, "diam_px", diam_px, "pixels_per_mm", round(pixels_per_mm, 4))
    annotated = image.copy()
    cv2.circle(annotated, (x, y), r, (0, 255, 0), 4)
    cv2.circle(annotated, (x, y), 3, (0, 0, 255), 3)
    cv2.putText(annotated, "PENNY DIAMETER", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.putText(annotated, "19.05 mm", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    window_name = "Phase 2 – Penny Diameter Detection (green circle)"
    cv2.imshow(window_name, annotated)
    cv2.waitKey(300)
    cv2.destroyAllWindows()
    return pixels_per_mm

def phase3_wire_segmentation(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0, 100, 50])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([160, 100, 50])
    upper2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    red = cv2.bitwise_or(mask1, mask2)
    contours, _ = cv2.findContours(red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("Error: No red string detected")
        return None
    main = max(contours, key=cv2.contourArea)
    if cv2.contourArea(main) < 500:
        print("Error: No red string detected")
        return None
    mask = np.zeros(red.shape, np.uint8)
    cv2.drawContours(mask, [main], -1, 255, -1)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    window_name = "Phase 3 – Red String Segmentation"
    cv2.imshow(window_name, mask)
    cv2.waitKey(300)
    cv2.destroyAllWindows()
    return mask

def phase4_wire_length_calculation(binary_image, pixels_per_mm, image=None):
    skel = np.zeros(binary_image.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    eroded = binary_image.copy()
    while True:
        temp = cv2.erode(eroded, element)
        temp2 = cv2.dilate(temp, element)
        temp2 = cv2.subtract(eroded, temp2)
        skel = cv2.bitwise_or(skel, temp2)
        eroded = temp.copy()
        if cv2.countNonZero(eroded) == 0:
            break
    contours, _ = cv2.findContours(skel, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    length_px = 0.0
    if contours:
        longest = max(contours, key=lambda c: cv2.arcLength(c, False), default=None)
        if longest is not None:
            length_px = cv2.arcLength(longest, False)
    if length_px < 5:
        print("Error: Red string length too short")
        return None
    length_mm = length_px / pixels_per_mm
    print("String length:", round(length_mm, 2), "mm (", round(length_px,1), "px )")
    if image is not None:
        annotated = image.copy()
        annotated[skel > 0] = (0, 255, 255)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            main = max(contours, key=cv2.contourArea)
            cv2.drawContours(annotated, [main], -1, (255, 0, 255), 5)
            x,y,w,h = cv2.boundingRect(main)
            cv2.rectangle(annotated, (x,y), (x+w, y+h), (0, 255, 255), 3)
            cv2.putText(annotated, "RED STRING", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        cv2.putText(annotated, "PENNY DIAMETER: 19.05 mm", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.putText(annotated, "STRING LENGTH: " + str(round(length_mm, 2)) + " mm", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        window_name = "Phase 4 – Red String Length Measurement"
        cv2.imshow(window_name, annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return length_mm

if __name__ == "__main__":
    print("MIT Assignment Module 6 - Penny + Red String Measurement (Phase 1-4). Live preview until Q (quit), c/space (capture), ESC.")
    image = phase1_camera_setup_and_capture()
    if image is not None:
        print("Phase 1 complete. Saved:", CAPTURED_IMAGE_PATH)
        pixels_per_mm = phase2_coin_detection_and_calibration(image)
        if pixels_per_mm is not None:
            print("Phase 2 complete. pixels_per_mm =", round(pixels_per_mm, 4))
            binary = phase3_wire_segmentation(image)
            if binary is not None:
                print("Phase 3 complete.")
                length = phase4_wire_length_calculation(binary, pixels_per_mm, image)
                if length is not None:
                    print("Phase 4 complete.")
                else:
                    print("Phase 4 failed.")
            else:
                print("Phase 3 failed to segment string.")
        else:
            print("Phase 2 failed to calibrate.")
    else:
        print("Phase 1 did not produce a confirmed image.")
