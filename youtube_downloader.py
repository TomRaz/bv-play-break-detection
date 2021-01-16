import os

from pytube import YouTube

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
dir_to_save_vids = os.path.join(CUR_DIR, "input_dir")


def download_video(url: str):
    i = 0

    # create the instance of the YouTube class
    video = YouTube(url)
    # print a summary of the selected video
    print('Summary:')
    print(f'Title: {video.title}')
    print(f'Duration: {video.length / 60:.2f} minutes')
    print(f'Rating: {video.rating:.2f}')
    print(f'# of views: {video.views}')
    return video.streams.get_by_itag(18).download(dir_to_save_vids)


video = download_video('https://www.youtube.com/watch?v=ItyphNrCG48&ab_channel=WinnersVolleyball1')
