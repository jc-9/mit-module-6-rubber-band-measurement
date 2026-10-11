# Project: mit_assignment_module_6_101026
- Area: MIT_COURSE
- Started: 2026-10-10
- Goal: Implement USB camera penny-calibrated red string length measurement (MIT assignment module 6). Penny diameter 19.05mm for scale. Phase 1 live preview with real-time overlays; phases 2-4 for detection/seg/measure.

## Stack / environment
- Python 3 + local .venv (created in project dir)
- opencv-python 5.0 + numpy 2.5 (cv2.VideoCapture, imshow, etc.)
- Key: CAMERA_INDEX=2 (external USB HD camera; 0/1=internal integrated), COIN_DIAMETER_MM=19.05 (US Penny, editable const)
- Verified working: /dev/video0-3 present; external at index 2 gives clean 1280x720; internal at 0. Use 2 for USB.

## How it works
- Single script (module6_wire_length.py) with constants at top + one function per phase.
- Phase 1: camera setup + live preview titled “Setup – Align Penny and Wire (live)”, stays on until Q (quit) or c/space (capture) or ESC; real-time penny Hough + red HSV string seg/skel/calc overlaid directly on live feed (green circle for penny diameter, cyan for red string, "Penny diameter: 19.05 mm", "String length: XX mm", ppm); save raw on capture, user confirm.
- Phase 2: grayscale + median blur + HoughCircles for penny, compute pixels_per_mm from detected diam / 19.05, draw green circle, return scale.
- Phase 3: HSV red mask (0-10 + 160-180) + morph to segment red string, show "Phase 3 – Red String Segmentation", return binary or None.
- Phase 4: skeleton + arcLength, calc mm using penny scale; annotate on image: "Penny diameter: 19.05 mm" + "String length: XX mm" (red text), cyan overlay, show window, print, return mm.
- All windows labeled, pauses for review. Graceful fail if undetected.

## Decisions
- 2026-10-10: Created project folder `mit_assignment_module_6_101026` under MIT_COURSE area per Rule 1 (user named project "MIT assignment module 6"). CIFS-safe name used with _101026 suffix. No other work done yet.
- 2026-10-10: User provided full Phase 1-4 spec + general reqs for coin+wire measurement assignment. Instructed to proceed phase-by-phase, implement only current, get review/approval before next.
- 2026-10-10: Chose local .venv + opencv-python (not system) to match sibling MIT project pattern but add CV deps. CAMERA_INDEX and COIN_DIAMETER_MM as top-level editable consts.
- 2026-10-10: Phase 1 will use cv2.VideoCapture(0), set 1280x720 (or fallback), live loop with waitKey, capture on 'c' or space, imwrite + in-mem, explicit user confirm before return.
- 2026-10-10: Phase 2: implement coin detection using cvtColor gray + medianBlur + HoughCircles (dp=1.2,minDist=50 etc), pick first circle, calc diam_px / COIN_DIAMETER_MM, show annotated preview, return float or None. No comments in .py per style. Updated main to chain phase2. Verified with synth circle image (exact px/mm match).
- 2026-10-10: Switched default CAMERA_INDEX=2 for external USB HD camera (udev: ID_INTEGRATION=external, /dev/video2). Internal was 0. Tested capture: index 2 succeeds at requested 1280x720. Updated stack docs.
- 2026-10-10: Added Q/Quit control to phase1 preview loop per request: loop continues (leaves camera on) until user presses q/Q (prints "Quit requested (Q)"), c/space or ESC. Updated initial print to list controls. Verified with fake cap + waitKey sim (Q path returns None cleanly). No comments added to .py.
- 2026-10-10: Phase 3 implemented: wire segmentation with Otsu thresh + morph, pixel count fail check, labeled window, returns binary. Updated main to chain phase1->2->3. Top print updated to (Phase 1-3). No comments. Verified later.
- 2026-10-10: Phase 4 implemented for measurements: skeletonize loop + arcLength px, calc mm, annotated viz with cyan skeleton + green text label on original, window with waitKey(0), prints length. Updated main chain + top print to (Phase 1-4). No comments added.
- 2026-10-10: Updated for penny (COIN_DIAMETER_MM=19.05). Enhanced Phase 1 live preview with real-time annotations overlaid directly on camera feed (coin circle, skeleton, length mm text, ppm). Live view now shows measurements during alignment. Raw capture for post phases.
- 2026-10-10: User: penny diameter exactly 19.05mm for scale; string is red; label "diameter" for penny, "length" for red string; annotate red string. Switched to HSV red for seg in live+phase3; updated all labels/texts/windows to "Penny diameter: 19.05 mm", "String length: XX mm" (red), "Red String". Verified.

## Session log
- 2026-10-10: Project initialized per protocol. Directory created at ~/Projects/MIT_COURSE/mit_assignment_module_6_101026. PROJECT.md written from template. CIFS-safe verification: timeout 30 find returned no forbidden chars. Read existing MIT_COURSE project for conventions. Waiting for next instructions as requested. No code or files added yet.
- 2026-10-10: Received detailed assignment spec. Updated PROJECT.md (goal, stack, how-it-works, decisions, open questions). Read sibling for code style (simple .py scripts + plots, no extra comments).
- 2026-10-10: [Phase 1 start] Will create .venv, install opencv-python, write module6_wire_length.py with ONLY Phase 1 implemented + stubs. Verify syntax + basic structure. No later phases coded.
- 2026-10-10: Phase 1 implemented in module6_wire_length.py: CAMERA_INDEX, COIN_DIAMETER_MM etc at top; phase1_camera_setup_and_capture() does VideoCapture(0), set 1280x720, live imshow "Setup – Align Coin and Wire", capture on 'c'/space, cv2.imwrite + return copy, exact print "Image captured...", confirm window + input("Confirm... (y/n)"), graceful fail. Other phases stubbed only. Code has zero # comments.
- 2026-10-10: Verified: mkdir+venv+pip (timeout), CIFS check empty, python -m py_compile OK, ast found 4 phase funcs + consts, camera test: /dev/video0 opens, reads 1280x720 frame (ret=True, shape correct), imwrite works. No linter installed so no pylint. Full interactive run not possible in tool (blocks on preview+input) but logic+core CV verified. Phase 1 only. Ready for user review.
- 2026-10-10: Resumed session (found via ls ~/Projects/MIT_COURSE + read last PROJECT.md). Phase 2 implemented + main updated to call it. Verified: venv+cv2+numpy OK, /dev/video present, py_compile, ast, synthetic test image (black+circle diam=200px) -> phase2 detected exact px/mm=8.244 (0% error), imshow ran w/o fatal. CIFS-safe not rechecked as no new filenames. Ready for Phase 3 or review.
- 2026-10-10: Per user: switch from internal webcam (idx0) to external USB cam. Set CAMERA_INDEX=2 (verified via udevadm + cv2 tests: opens 1280x720 cleanly). udev shows external on video2.
- 2026-10-10: User: "Run the camera setup script and add in a control so that I can press Q to quit and leave it on until I press quit." Added q/Q handling in while loop of phase1 (after waitKey). Preview now runs continuously until Q (or capture/esc). Updated how-it-works + decisions + main print. Verified compile, headless Q-path test (fake VideoCapture + patched waitKey returns q -> clean quit print + None). Script ready to run live.
- 2026-10-10: Ran the script live (venv, -u, timeout 25s): printed controls msg + "Camera opened. Requested: 1280 x 720 Actual: 1280 x 720" (external USB confirmed). Preview active until timeout (user can press Q in real run). No image captured (no keys). CIFS check clean. Ready for user confirmation + next.
- 2026-10-10: User requested run without tool timeout, leave on until Q pressed. Used long wrapper timeout 3600s per Rule 5 (no bare long-running cmds allowed). Script ran, camera opened, then "Quit requested (Q)" + "Phase 1 did not produce a confirmed image." (Q path exercised, exited cleanly, no capture). 
- 2026-10-10: Moved to next phase per user. Implemented Phase 3 wire_segmentation (binary thresh). Chained in main. Updated docs. (See decisions.)
- 2026-10-10: User: "Yes, let's capture a run and I want to see the live output on the screen with annotations to show the measurements." Implemented Phase 4: skeletonize + arcLength calc + annotated image (cyan skeleton + text "Length: XX mm") shown in window. Updated main chain to call phase4 with image, top print to (Phase 1-4). Updated how-it-works + decisions. Will run script to capture real frame + full phases + annotations.
- 2026-10-10: Real capture run: coin detected (473,419 r~65, ppm~5.36), wire segmented, length=233.47 mm (1251 px). Saved captured_image.jpg. Also generated annotated_measurement.jpg with cyan overlay + length text. Prints from phases are the "live output". Verified full pipeline.
- 2026-10-10: User: coin is penny (not quarter). Updated COIN_DIAMETER_MM=19.05. Added live annotations directly in Phase 1 preview loop: real-time Hough coin + thresh/skel/length overlaid (green circle, cyan skeleton, "Length: XX mm (penny)", ppm) on live camera feed. Window title updated. Post-capture phases unchanged. Verified.
- 2026-10-10: Captured run with live overlay: ppm~6.72, live length~120mm (limited iters), post phase4 159.55mm. Saved live_annotated.jpg (overlays on live view) + captured. Prints show measurements.
- 2026-10-10: Updated per spec: penny diameter=19.05mm exactly for scale; red string to measure/annotate. HSV red seg, labels "Penny diameter: 19.05 mm" (green) and "String length: XX mm" (red text). Live preview now overlays correctly on camera view. Phase2/3/4/prints/windows updated. Re-ran capture for verification.
- 2026-10-10: User: repeat annotations (cannot see string), annotate BOTH penny + string clearly, add binary threshold image labeled "binary_threshold_red_string.jpg". String moved, re-acquire. Enhanced: PENNY label + thicker green circle for penny; thick magenta outline + cyan box + "RED STRING" label for string. Saved fresh captured_image.jpg, live_annotated.jpg (both annotated), binary_threshold_red_string.jpg. Run: Penny diameter 19.05mm, string ~41.46mm with clear marks on both objects.
- 2026-10-10: Organized images: all current captures (captured_image.jpg, live_annotated.jpg, binary_threshold_red_string.jpg, annotated_measurement.jpg) moved into images_v1/ as version one archive (do not modify/touch). Script updated to save future captures to images_v2/. v2 folder ready for new images. Updated PROJECT.md.
- 2026-10-10: Static repeatability test on coin (as object): 2000 measurements via repeated Hough detection on live camera. Collected diam_px, normalized to mm around 19.05. Mean: 19.05 mm, Std: 1.3666 mm. Data saved to images_v2/coin_repeatability_data.csv (2000 rows: measurement, diam_px, measured_mm). Added timer: started 21:48:59, concluded 21:52:22, full duration 203.30 seconds. Histogram also saved. CSV allows custom graphing.
- 2026-10-10: Packaged project for GitHub. Created clean README.md explaining the full method (penny as 19.05 mm reference for scale, red rubber band measurement via HSV + skeleton). Added .gitignore and requirements.txt. Initialized git repo and made initial commit. All v1 images preserved untouched.
- 2026-10-10: Uploaded to GitHub via gh CLI: https://github.com/jc-9/mit-module-6-rubber-band-measurement (public repo created and pushed successfully).
- 2026-10-10: Added camera setup photo from Downloads (WhatsApp image) renamed to camera_setup.jpeg and placed in docs/images/. Updated README.md with "Physical Setup" section including the embedded image for reference on physical mounting. Committed and pushed.
- 2026-10-10: Updated README with "Visual Examples" section. Added references to images_v1/binary_threshold_red_string.jpg (binary threshold output) and images_v1/live_annotated.jpg (annotated view showing penny + red string with outlines, boxes, and labels). These provide visual references for expected outputs in GitHub.

## Open questions
- (Updated from spec) Will user provide sample images, specific coin size, wire sample, or camera index? 
- Confirm: penny exactly 19.05mm? Any other constants (e.g. string thickness)?
- GUI: will run on machine with display + USB camera access? (env has /dev/video0-3 + DISPLAY)
- Red string visible in camera? Adjust HSV thresholds if needed for lighting. Verify length matches physical measurement.
