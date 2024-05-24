from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from download import download_with_ytdlp, ytdlp_options
from login import alurasession, BeautifulSoup, courses, data_schools
from utils import re, clear_folder_name, os, create_folder


def get_modules(path, courses_data):
  data_sections = {}
  for n, (course_title, course_data) in enumerate(courses_data.items(), start=1):
    course_title = f'{n:03d} - {clear_folder_name(course_title)}' 
    path_module = create_folder(os.path.join(path, course_title))
    response = alurasession.get(course_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all('a', class_='courseSectionList-section')
    data_sections[path_module] = sections
  return data_sections


def get_section_href(sections):
  for section in sections:
    print(f'https://cursos.alura.com.br{section["href"]}')


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
    for n, video in enumerate(response, start=1):
      if video['quality'] == 'hd':
        ydl_opts = ytdlp_options(os.path.join(path, f'{n:03d} - aula'), alurasession)
        download_with_ytdlp(ydl_opts, video['mp4'])


def get_content(soup, path):
  contents = soup.find_all('div', class_='formattedText', attrs={'data-external-links': ''})
  if contents:
    for n, content in enumerate(contents, start=1):
      folder_path = create_folder(os.path.join(path, 'descricao'))
      folder_path = os.path.join(folder_path, f'{n:03d} - aula.html')
      if not os.path.exists(folder_path):
        with open(folder_path, 'w', encoding='utf-8') as file:
          file.write(content.prettify())


def process_single_lesson(lesson_path, lesson_link):
  response = alurasession.get(lesson_link)
  soup = BeautifulSoup(response.text, 'html.parser')
  get_videos(soup, lesson_path, lesson_link)
  get_content(soup, lesson_path)


def process_lessons(lessons):
  with ThreadPoolExecutor(max_workers=3) as executor:
    future_tasks = {executor.submit(process_single_lesson, lesson_path, lesson_link): (lesson_path, lesson_link) for lesson_path, lesson_link in lessons.items()}
    for future in future_tasks:
      future.result()


def data_lessons(data_lessons):
  lessons_info = {}
  for n, (lesson_title, lesson_data) in enumerate(data_lessons.items(), start=1):
    lesson_title = f'{n:03d} - {clear_folder_name(lesson_title)}'
    lesson_link = f'https://cursos.alura.com.br{lesson_data["link"]}'
    lesson_path = create_folder(os.path.join(lesson_data['path'], clear_folder_name(lesson_title)))
    lessons_info[lesson_path] = lesson_link
  return lessons_info


def process_modules(title, link, path):
  path_module = create_folder(os.path.join(path, clear_folder_name(title)))
  response = alurasession.get(link)
  soup = BeautifulSoup(response.text, 'html.parser')
  tasks = soup.find_all('a', class_=re.compile(r'^task-menu-nav-item-link-'))
  videos = {}

  for task in tasks:
    href = task.get('href')
    title = task.find('span', class_='task-menu-nav-item-title').get('title')
    videos[title] = {'link': href, 'path': path_module}
  return videos


def data_modules(sections, progress_bar):
  data = {}
  for path, sections_data in sections.items():
    for n, section in enumerate(sections_data, start=1):
      title, link = decompose_object_tags(section, n)
      data[title] = {'link': link, 'path': path}
      modules = process_modules(title, link, path)
      data = data_lessons(modules)
      lessons = process_lessons(data)
    progress_bar.update(1)


if __name__ == '__main__':
  total_courses = sum(len(course_info) for _, course_info in courses.items())
  progress_bar = tqdm(total=total_courses, desc="Processing courses")
  for n, (path, course_info) in enumerate(courses.items(), start=1):
    path_school = create_folder(os.path.join(os.getcwd(), path))
    sections = get_modules(path_school, course_info)
    data_modules(sections, progress_bar)