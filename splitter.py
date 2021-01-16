import os
from enum import Enum
from multiprocessing import Pool

import imutils
from cv2 import cv2

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
skip_test = 0

MIN_FRAMES_TO_CONSIDER_AS_HAND = 5

# skip_test = 0
DEBUG = False


class State(Enum):
    play = "play"
    in_break = "in_break"


def process_video(args):
    file_path, skip_minutes = args
    vid_cap = cv2.VideoCapture(file_path, )
    video_name = os.path.abspath(file_path)
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    print(f"Fps is {fps}")

    skip_frames = skip_minutes * 60 * fps + skip_test
    vid_cap.set(cv2.CAP_PROP_POS_FRAMES, skip_frames)
    i = skip_test
    first_frame = None
    out_vid = None
    prev_out_vid = None
    state = State.in_break

    last_on_frame_index = None

    dir_to_save_vids = os.path.join(CUR_DIR, "test", video_name.split(".")[0])
    os.makedirs(dir_to_save_vids, exist_ok=True)
    buffer_frames_left = 0
    cnt_hand_raise = 0
    while vid_cap.isOpened():
        i += 1
        success, image = vid_cap.read()
        height, width, channels = image.shape

        should_wait_for_input = False

        referee, referee_start, referee_end = extract_referee(image)
        if first_frame is None:
            first_frame = referee
            copy = referee.copy()
            cv2.putText(copy, "Initial frame", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow('frame', image)
            cv2.waitKey()
            continue
        check_hand = True
        distance_between_frames = last_on_frame_index and i - last_on_frame_index
        if prev_out_vid is not None:
            buffer_frames_left -= 1
            if buffer_frames_left == 0:
                prev_out_vid = None
            check_hand = False
        if not DEBUG:
            save_clean_image([out_vid, prev_out_vid], image)

        if distance_between_frames and distance_between_frames <= 80:
            check_hand = False

        hand_bounding_box = check_hand and get_raising_hand(referee, first_frame)

        if hand_bounding_box:
            cnt_hand_raise += 1
            if cnt_hand_raise > MIN_FRAMES_TO_CONSIDER_AS_HAND:
                (x, y, w, h) = hand_bounding_box
                x = referee_start[0] + x
                y = referee_start[1] + y
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                last_on_frame_index = i
                should_wait_for_input = True
                if state == State.in_break:
                    if out_vid:
                        if prev_out_vid:
                            prev_out_vid.release()
                        prev_out_vid = out_vid
                    print("start play")
                    state = state.play
                    if not DEBUG:
                        out_vid = cv2.VideoWriter(os.path.join(dir_to_save_vids, f"{i}-play.mp4"), fourcc, fps, (int(width), int(height)))
                    buffer_frames_left = 40
                elif state == State.play:
                    if out_vid:
                        if prev_out_vid:
                            prev_out_vid.release()
                        prev_out_vid = out_vid
                    print("Start break")
                    state = state.in_break
                    if not DEBUG:
                        out_vid = cv2.VideoWriter(os.path.join(dir_to_save_vids, f"{i}-break.mp4"), fourcc, fps, (int(width), int(height)))
                    buffer_frames_left = 40
        else:
            cnt_hand_raise = 0

        # # loop over the contours
        if DEBUG:
            cv2.putText(image, str(state), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow('frame', image)

            if should_wait_for_input:
                cv2.waitKey()
            else:
                cv2.waitKey(delay=10)


def extract_referee(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape
    referee_start = (width - 100, height - 80)
    referee_end = (width, height - 50)
    referee = gray[referee_start[1]:referee_end[1], referee_start[0]:referee_end[0]]
    referee = cv2.GaussianBlur(referee, (21, 21), 0)
    return referee, referee_start, referee_end


def get_raising_hand(referee, first_frame):
    frame_delta = cv2.absdiff(first_frame, referee)
    thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=1)

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    for c in contours:
        # if the contour is too small, ignore it
        (x, y, w, h) = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        if DEBUG:
            print(area, w / h)
        if not (250 < area < 1000) or w / h < 1.35:
            # if DEBUG and area > 150:
            #     cv2.imshow('frame', referee)
            #     cv2.waitKey()
            #     cv2.imshow('frame', thresh)
            #     cv2.waitKey()
            continue
        return (x, y, w, h)
    return False


def save_clean_image(vid_streams, image):
    height, width, channels = image.shape
    image[height - 90:height, width - 100:width] = 255
    image[height - 50:height, 0:300] = 255

    for vid in vid_streams:
        if vid is not None:
            vid.write(image)


videos_to_process = [("Winners Beach Volleyball Court 1 04122020 Part 4.mp4", 18),
                     ("Winners Beach Volleyball Court 1 05012021 Part 2.mp4", 17.5),
                     ("Winners Beach Volleyball Court 1 07122020 Part 2.mp4", 7.3),
                     ("Winners Beach Volleyball Court 1 16122020 Part 4.mp4", 5.98)]

if __name__ == '__main__':
    with Pool(4) as p:
        print(p.map(process_video, videos_to_process))

# process_video(("Winners Beach Volleyball Court 1 16122020 Part 4.mp4", 5.98))
