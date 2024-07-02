import yt_dlp
from utils import os, SilentLogger, logger


def download_with_ytdlp(output_folder, media, session=None):
  ydl_opts = {
    'logger': SilentLogger(media, f'{output_folder}.%(ext)s'),
    'merge_output_format': 'mp4',
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': f'{output_folder}.%(ext)s',
    'quiet': True,
    'continuedl': True,
    'no_progress': True,
    'no_overwrites': True,
    'windows_filenames': True,
    'retries': 50,
    'trim_file_name': 249,
    'fragment_retries': 50,
    'extractor_retries': 50,
    'file_access_retries': 50,
    'concurrent_fragment_downloads': 10,
  }
  if session:
    ydl_opts['http_headers'] = {'referer': session.headers['referer'], 'Upgrade-Insecure-Requests': '1'}
  while True:
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([media])
        return
    except yt_dlp.utils.DownloadError as e:
      msg = f'''Verifique manualmente, se não baixou tente novamente mais tarde: {ydl_opts['outtmpl']} ||| {media} ||| {e}'''
      logger(msg, warning=True)
      return