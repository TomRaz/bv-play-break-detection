from email_sender import SendMessage

from_email = "rom.zar90@gmail.com"


def notify_user(video_link: str, video_name, email: str):
    msg = f"""
    Hi there!
    Your video is ready and break free, enjoy!\n
    {video_link}
    """
    SendMessage(from_email, email, f"Processed beach volleyball video for {video_name} is ready!", msg, msg)
