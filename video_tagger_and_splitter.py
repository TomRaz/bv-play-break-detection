import os

import cv2

# load the trained model and label binarizer from disk
input_file = "/Users/tom/Projects/bv-play-break-detection/data/bvb after parctice 08.07.2021.mp4"
video_name = "first"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

vs = cv2.VideoCapture(input_file)
(W, H) = (None, None)
count = 0
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
dir_to_save_vids = os.path.join(CUR_DIR, "data")
dir_to_save_vids = os.path.join(dir_to_save_vids, "real")
print(dir_to_save_vids)
fps = vs.get(cv2.CAP_PROP_FPS)

out_vid = None
should_close_last_vid = False
is_break = True
start_outputing = False
vid_type = "break"
while True:
    # read the next frame from the file
    (grabbed, frame) = vs.read()

    height, width, channels = frame.shape
    count += 1
    copy = frame.copy()
    color = (0, 0, 255) if vid_type == "break" else (0, 255, 0)
    cv2.putText(copy, vid_type, (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,color, 2)
    cv2.imshow("Output", copy)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    if key == ord("s"):
        count += 120
        vs.set(1, count)
        continue
    if key == ord("g"):
        start_outputing = True
    if not start_outputing:
        continue

    if key == ord("1"):
        should_close_last_vid = True
        is_break = not is_break

    else:
        should_close_last_vid = False

    if should_close_last_vid:
        out_vid.release()
        out_vid = None
    if out_vid is None:
        vid_type = "break" if is_break else "play"
        path = os.path.join(dir_to_save_vids, f"{video_name}-{count}-{vid_type}.mp4")
        print(path)
        out_vid = cv2.VideoWriter(path, fourcc, fps, (int(width), int(height)))
    out_vid.write(frame)

# release the file pointers
print("[INFO] cleaning up...")
# writer.release()
vs.release()
