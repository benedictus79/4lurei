import yt_dlp
from utils import SilentLogger, logger


def ytdlp_options(output_folder, session=None):
  options = {
    'format': 'bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
    'outtmpl': f'{output_folder}.%(ext)s',
    'quiet': True,
    'no_progress': True,
    'overwrites': False,
    'continuedl': True,
    'logger': SilentLogger(),
    'concurrent_fragment_downloads': 10,
    'fragment_retries': 50,
    'file_access_retries': 50,
    'retries': 50,
    'extractor_retries': 50,
    'trim_file_name': 249,
  }
  if session:
    options['http_headers'] = session.headers
  
  return options


def download_with_ytdlp(ydl_opts, media):
  while True:
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([media])
        return
    except yt_dlp.utils.DownloadError as e:
      msg = f'''Verifique manualmente, se não baixou tente novamente mais tarde: {ydl_opts['outtmpl']} ||| {media} ||| {e}'''
      logger(msg, warning=True)
      return