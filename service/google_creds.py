import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

CLIENT_SECRET_FILE = os.path.join(DIR_PATH, 'client_secret.json')


def get_google_secret_file_path():
    return CLIENT_SECRET_FILE
