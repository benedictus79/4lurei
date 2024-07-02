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

  Author: Alex4ndria Team
  Community: https://t.me/+DoZ_EeKWN0NhY2Ix
  Script: {name}
  Version: {version}
  """
  print(alexandria.format(name='4lurei', version='Alpha 0.6'))


def clear_screen():
  os.system('cls || clear')


def create_folder(folder_name):
  path = os.path.join(os.getcwd(), folder_name)

  if not os.path.exists(path):
    os.mkdir(path)

  return path


def clear_folder_name(name):
  sanitized_name = re.sub(r'[<>:"/\\|?*]', ' ', name)
  sanitized_name = re.sub(r'\s+', ' ', sanitized_name)
  sanitized_name = re.sub(r'\.+$', '', sanitized_name)
  return sanitized_name.strip()


def logger(message, error=None, warning=None):
  if error:
    log_to_file('4lurei_erros.txt', message)
  if warning:
    log_to_file('4lurei_avisos.txt', message)


def log_to_file(filename, message):
  timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
  with open(filename, 'a', encoding='UTF-8') as file:
    file.write(f'{timestamp} - {message}\n')


class SilentLogger(object):
  def __init__(self, url=None, output_path=None):
    self.url = url
    self.output_path = output_path

  def debug(self, msg):
    pass

  def warning(self, msg):
    logger(f"WARNING: {msg} - URL: {self.url}, Path: {self.output_path}")

  def error(self, msg):
    logger(f"ERROR: {msg} - URL: {self.url}, Path: {self.output_path}")