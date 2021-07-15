import os

from pytube import YouTube

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
dir_to_save_vids = os.path.join(CUR_DIR, "input_dir")


def download_video(url: str, dir_to_save: str):
    print(f"downloading video from {url}, saving to {dir_to_save}")
    video = YouTube(url)
    file_path = video.streams.first().download(dir_to_save)
    print(f"finished downloading video {video.title}")
    return file_path, video.title
