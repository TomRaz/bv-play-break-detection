from collections import deque

import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = None

THRESHOLD = 0.3


class C3DCnnModelWrapper:
    SNIPPET_FRAMES_LENGTH = 16

    def __init__(self, model):
        self.model = model
        # self.previous_frames = deque(maxlen=self.SNIPPET_FRAMES_LENGTH)

    def predict(self, frames):
        global model
        if not model:
            model = load_model("/Users/tom/Downloads/3d.model", custom_objects={"lr": None})
        frames = [cv2.resize(frame, (112, 112)) for frame in frames]
        buf = np.empty((16, 112, 112, 3), np.dtype('uint8'))
        for ind, frame in enumerate(frames):
            buf[ind] = frame
        input = np.array(buf, dtype=np.float32)
        input_array = np.array([input], dtype=np.float32)
        return model.predict(input_array)[0]


class ImageCnnModelWrapper:
    SNIPPET_FRAMES_LENGTH = 1
    mean = np.array([123.68, 116.779, 103.939][::1], dtype="float32")

    def __init__(self, model):
        self.model = model

    def predict(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (224, 224)).astype("float32")
        frame -= self.mean
        return model.predict(np.expand_dims(frame, axis=0))[0]


def process_video(input_file, output_file, trim_breaks=True, show_label=False):
    Q = deque(maxlen=6)

    vs = cv2.VideoCapture(input_file)
    writer = None
    (W, H) = (None, None)
    model_wrapper = C3DCnnModelWrapper(model)

    # loop over frames from the video file stream
    frame_ind = 0
    cont = True
    while cont:

        frame_ind += 1
        if frame_ind == 20:
            break
        # output = frame.copy()
        frames = []
        for i in range(model_wrapper.SNIPPET_FRAMES_LENGTH):
            (grabbed, frame) = vs.read()

            if not grabbed:
                cont = False
                break
            frames.append(frame)

        preds = model_wrapper.predict(frames)
        Q.append(preds)

        results = np.array(Q).mean(axis=0)
        label = "play" if results > THRESHOLD else "break"

        # check if the video writer is None
        if writer is None:
            # initialize our video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            if W is None or H is None:
                (H, W) = frames[0].shape[:2]
            writer = cv2.VideoWriter(output_file, fourcc, 30, (W, H), True)

        if trim_breaks and label == "break":
            continue
        for frame in frames:
            if show_label:
                color = (0, 255, 0) if label == "play" else (0, 0, 255)
                cv2.putText(frame, label, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.25, color, 5)
            writer.write(frame)

        # show the output image
        # cv2.imshow("Output", output)
        # key = cv2.waitKey(1) & 0xFF
        #
        # # if the `q` key was pressed, break from the loop
        # if key == ord("q"):
        #     break

    # release the file pointers
    print("[INFO] cleaning up...")
    if writer:
        writer.release()
    vs.release()

#
