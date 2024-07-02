from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from download import download_with_ytdlp
from login import alurasession, BeautifulSoup, courses
from utils import re, datetime, clear_folder_name, os, create_folder


def get_modules(path, courses_data):
  for n, (course_title, course_data) in enumerate(tqdm(courses_data.items(), desc='Processing Courses', total=len(courses_data.items())), start=1):
    data_sections = {}
    course_title = f'{n:03d} - {clear_folder_name(course_title)}' 
    path_module = create_folder(os.path.join(path, course_title))
    response = alurasession.get(course_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all('a', class_='courseSectionList-section')
    data_sections[path_module] = sections
    data_modules(data_sections)


def decompose_object_tags(section, n):
  for div in section.find_all('div', class_='courseSectionList-sectionTitle bootcamp-text-color'):
    object_tag = div.find('object')
    if object_tag:object_tag.decompose()
    return print_section_details(div, section, n)


def print_section_details(div, section, n):
  section_title = div.get_text(strip=True)
  section_title = f'{n:03d} - {section_title}'
  return section_title, f'https://cursos.alura.com.br{section["href"]}'


def get_videos(soup, path, lesson_link):
  if soup.find('section', class_='video-container', id='video'):
    response = alurasession.get(f'{lesson_link}/video').json()
    for video in response:
      if video['quality'] == 'hd':
        output_folder = os.path.join(path, 'aula')
        download_with_ytdlp(output_folder, video['mp4'], alurasession)
      elif video['quality'] == 'sd':
        output_folder = os.path.join(path, 'aula')
        download_with_ytdlp(output_folder, video['mp4'], alurasession)


def get_content(soup, path):
  contents = soup.find_all('div', class_='formattedText', attrs={'data-external-links': ''})
  questions = soup.find('ul', class_='alternativeList')
  suffix = 'questionario.html' if questions else 'texto.html'
  if contents:
    content = contents[0]
    file_path = os.path.join(path, suffix)
    if not os.path.exists(file_path):
      with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content.prettify())
        if questions:
          buttons = questions.find_all('button', class_='alternativeList-item-opinionButton')
          for button_tag in buttons:
            button_tag.decompose()
          file.write(questions.prettify()) 


def process_lessons(lessons):
  for lesson_path, lesson_link in lessons.items():
    response = alurasession.get(lesson_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    get_videos(soup, lesson_path, lesson_link)
    get_content(soup, lesson_path)


def data_lessons(index, data):
  for lesson_title, lesson_data in data.items():
    lessons_info = {}
    lesson_title = f'{index:03d} - {clear_folder_name(lesson_title)}'
    lesson_link = f'https://cursos.alura.com.br{lesson_data["link"]}'
    lesson_path = create_folder(os.path.join(lesson_data['path'], clear_folder_name(lesson_title)))
    lessons_info[lesson_path] = lesson_link
    process_lessons(lessons_info)


def process_modules(title, link, path):
  path_module = create_folder(os.path.join(path, clear_folder_name(title)))
  response = alurasession.get(link)
  soup = BeautifulSoup(response.text, 'html.parser')
  tasks = soup.find_all('a', class_=re.compile(r'^task-menu-nav-item-link-'))

  with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for i, task in enumerate(tasks, start=1):
      videos = {}
      href = task.get('href')
      title = task.find('span', class_='task-menu-nav-item-title').get('title')
      videos[title] = {'link': href, 'path': path_module}
      future = executor.submit(data_lessons, i, videos)
    for future in futures:
      future.result


def list_modules(path, section_data):
  for n, section in enumerate(section_data, start=1):
    data = {}
    title, link = decompose_object_tags(section, n)
    data[title] = {'link': link, 'path': path}
    process_modules(title, link, path)


def data_modules(sections):
  for path, sections_data in sections.items():
    list_modules(path, sections_data)


if __name__ == '__main__':
  start_time = datetime.now()
  print(f'Início da execução: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
  for path, course_info in courses.items():
    path_school = create_folder(os.path.join(os.getcwd(), path))
    sections = get_modules(path_school, course_info)
  end_time = datetime.now()
  print(f'Fim da execução: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
  input("Pressione Enter para fechar...")