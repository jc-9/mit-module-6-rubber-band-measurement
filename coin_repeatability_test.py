import cv2
import numpy as np
import os
import time
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CAMERA_INDEX = 2
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
COIN_DIAMETER_MM = 19.05
NUM_MEASUREMENTS = 2000
IMAGES_DIR = "images_v2"
os.makedirs(IMAGES_DIR, exist_ok=True)

start_time = time.time()
print("Test started at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))

diameters_px = []
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
for i in range(NUM_MEASUREMENTS):
    ret, frame = cap.read()
    if not ret:
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    small = cv2.resize(gray, (640, 360))
    circles = cv2.HoughCircles(small, cv2.HOUGH_GRADIENT, dp=1.2, minDist=25, param1=50, param2=30, minRadius=5, maxRadius=150)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        if len(circles) > 0:
            x, y, r = circles[0]
            diam_px = 2 * r * 2
            if diam_px > 10:
                diameters_px.append(diam_px)
    if i % 100 == 0:
        import sys
        sys.stdout.flush()
cap.release()

diameters_px = np.array(diameters_px)
if len(diameters_px) == 0:
    print("No successful measurements")
else:
    mean_px = np.mean(diameters_px)
    std_px = np.std(diameters_px)
    measurements_mm = diameters_px * (COIN_DIAMETER_MM / mean_px)
    mean_mm = np.mean(measurements_mm)
    std_mm = np.std(measurements_mm)
    print("Successful measurements:", len(measurements_mm))
    print("Mean diameter:", round(mean_mm, 4), "mm")
    print("Std dev:", round(std_mm, 4), "mm")

    csv_path = os.path.join(IMAGES_DIR, "coin_repeatability_data.csv")
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["measurement", "diam_px", "measured_mm"])
        for idx, d_px in enumerate(diameters_px, 1):
            m_mm = d_px * (COIN_DIAMETER_MM / mean_px)
            writer.writerow([idx, d_px, m_mm])
    print("Data saved to", csv_path)

    plt.figure(figsize=(16, 6))
    plt.hist(measurements_mm, bins=100, color='blue', edgecolor='black', alpha=0.7)
    plt.axvline(mean_mm, color='red', linestyle='dashed', linewidth=2, label="Mean = " + str(round(mean_mm, 4)) + " mm")
    plt.axvline(mean_mm + std_mm, color='green', linestyle='dashed', linewidth=1, label="+1 sigma")
    plt.axvline(mean_mm - std_mm, color='green', linestyle='dashed', linewidth=1, label="-1 sigma")
    plt.xlim(mean_mm - 4*std_mm, mean_mm + 4*std_mm)
    plt.title("Coin Diameter Repeatability Histogram (n=" + str(len(measurements_mm)) + ")")
    plt.xlabel("Diameter (mm)")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    hist_path = os.path.join(IMAGES_DIR, "coin_diameter_repeatability_histogram.png")
    plt.savefig(hist_path, bbox_inches='tight', pad_inches=0.05)
    print("Histogram saved to", hist_path)

    end_time = time.time()
    duration = end_time - start_time
    print("Test concluded at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    print("Full duration: {:.2f} seconds".format(duration))
