from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from download import download_with_ytdlp
from login import alurasession, BeautifulSoup, courses
from utils import re, clear_folder_name, os, create_folder


def get_modules(path, courses_data):
  data_sections = {}
  for n, (course_title, course_data) in enumerate(tqdm(courses_data.items(), desc='Processing Courses', total=len(courses_data.items())), start=1):
    course_title = f'{n:03d} - {clear_folder_name(course_title)}' 
    path_module = create_folder(os.path.join(path, course_title))
    response = alurasession.get(course_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all('a', class_='courseSectionList-section')
    data_sections[path_module] = sections
    data_modules(data_sections)


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


def data_modules(sections):
  data = {}
  for path, sections_data in sections.items():
    for n, section in enumerate(sections_data, start=1):
      title, link = decompose_object_tags(section, n)
      data[title] = {'link': link, 'path': path}
      modules = process_modules(title, link, path)
      data = data_lessons(modules)
      process_lessons(data)


if __name__ == '__main__':
  total_courses = sum(len(course_info) for _, course_info in courses.items())
  for path, course_info in courses.items():
    path_school = create_folder(os.path.join(os.getcwd(), path))
    sections = get_modules(path_school, course_info)