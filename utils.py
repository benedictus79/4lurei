import os
import re
from datetime import datetime


def alexandria_ascii_art():
  alexandria = r"""

 _  _   _    _   _ ____  _____ ___ 
| || | | |  | | | |  _ \| ____|_ _|
| || |_| |  | | | | |_) |  _|  | | 
|__   _| |__| |_| |  _ <| |___ | | 
   |_| |_____\___/|_| \_\_____|___|

  Author: Bendictus | Xanarcry ;( | doiscafe | sukuna
  Community: https://t.me/+7imfib1o0CQwNmUx5
  Script: {name}
  Version: {version}
  """
  print(alexandria.format(name='4lurei', version='Alpha 0.1'))


def clear_screen():
  os.system('cls || clear')


def create_folder(folder_name):
  path = os.path.join(os.getcwd(), folder_name)

  if not os.path.exists(path):
    os.mkdir(path)

  return path


def clear_folder_name(name, is_file=None, ext=''):
  if is_file:
    name, ext = os.path.splitext(name)
  sanitized_base = re.sub(r'[<>:."/\\|?*]|\s+|\.$', ' ', name).strip()
  return sanitized_base + ext if ext else sanitized_base


def logger(message, error=None, warning=None):
  if error:
    log_to_file('hotm4rtei_erros.txt', message)
  if warning:
    log_to_file('hotm4rtei_avisos.txt', message)


def log_to_file(filename, message):
  timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
  with open(filename, 'a', encoding='UTF-8') as file:
    file.write(f'{timestamp} - {message}\n')


class SilentLogger(object):
  def debug(self, msg):
    pass

  def warning(self, msg):
    if 'If this is a livestream,' in str(msg):return
    logger(msg, warning=True)

  def error(self, msg):
    if 'HTTP Error 403' in str(msg):return
    if 'No such file or directory' in str(msg):return
    logger(msg, error=True)