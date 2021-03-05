import os
import shutil

from cv2 import cv2
from os import listdir
from os.path import isfile, join
CUR_DIR = os.path.dirname(os.path.realpath(__file__))


def tag_dir(dir_path):

    onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f)) if f.endswith(".mp4")]
    onlyfiles.sort(key=lambda x:int(x.split("-")[0]))
    os.makedirs(os.path.join(dir_path, "tagged"), exist_ok=True)
    for vid in onlyfiles:
        print(vid)
        full_path = os.path.join(dir_path, vid)
        vid_cap = cv2.VideoCapture(full_path)
        key = None
        last_image = None
        while vid_cap.isOpened():
            success, image = vid_cap.read()
            if success:
                last_image = image
                cv2.imshow("frame", image)
                key = cv2.waitKey(10)
                if key != -1:
                    break
            else:
                break
        if not key or key == -1:
            cv2.imshow("frame", last_image)
            key = cv2.waitKey()
        name = vid.replace(".mp4", "").replace("-play", "").replace("-break", "")
        tag_name = "play" if key == 49 else "break"
        shutil.move(full_path, os.path.join(dir_path, "tagged", f"{name}-{tag_name}.mp4"))

        # num_of_frames = vid_cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # for ind, frame in enumerate(np.linspace(0, num_of_frames, 10)):
        #     vid_cap.set(cv2.CAP_PROP_POS_FRAMES, frame-1)
        #     success, image = vid_cap.read()
        #     cv2.imshow(f"frame{ind+1}", image)
        # print(cv2.waitKey())


tag_dir(os.path.join(CUR_DIR, "data", "Winners Beach Volleyball Court 1 05012021 Part 2"))
