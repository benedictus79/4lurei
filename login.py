import requests
from bs4 import BeautifulSoup
from utils import clear_folder_name, os, alexandria_ascii_art, clear_screen, create_folder

alurasession = requests.Session()

def credentials():
  alexandria_ascii_art()
  email = input('Login: ')
  password = input('Senha: ')
  clear_screen()
  return email, password

def login(email, password):
  headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'pt-BR,pt;q=0.5',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://cursos.alura.com.br',
    'priority': 'u=0, i',
    'referer': 'https://cursos.alura.com.br/loginForm',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  }

  data = f'username={email}&password={password}&uriOnError='

  response = alurasession.post('https://cursos.alura.com.br/signin', headers=headers, data=data)
  all_courses_link = f'https://cursos.alura.com.br/courses'
  http = alurasession.get(all_courses_link)
  soup = BeautifulSoup(http.text, 'html.parser')
  select = soup.find('select', class_='search__select')
  schools = []
  if select:
      options = select.find_all('option')
      for option in options:
          schools.append(option['value'])
  return schools


def choose_schools(schools):
  data_schools = {}
  print("Escolas disponíveis:")
  for i, schools_title in enumerate(schools, start=1):
    if i == 1:
      schools[0], schools_title = 'todos', 'todos'
    print(f"{i}. {schools_title}")
  choice = int(input("Escolha o número do curso que deseja visualizar: "))
  if i == 1:schools_title='todos'
  selected_schools_title = schools[int(choice) - 1]
  path_school = os.path.join(os.getcwd(), selected_schools_title)
  selected_course_link = f'https://cursos.alura.com.br/courses?categoryUrlName={selected_schools_title}'
  if choice == 1:
    selected_course_link = f'https://cursos.alura.com.br/courses'
  data_schools[selected_schools_title] = {'path': path_school, 'link': selected_course_link}
  print(f"Você selecionou: {selected_schools_title} - Link: {selected_course_link}")
  return data_schools

def total_pages(pages):
  if pages:
    last_link = pages[-1]
    return last_link.get_text()
    
def list_items(items):
  courses = {}
  for item in items:
    course_link = item.find('a', class_='course-card__course-link')['href']
    course_title = item.find('span', class_='course-card__name').text
    courses[course_title] = f'https://cursos.alura.com.br{course_link}'
  return courses


def pagination(soup, name, total_pages):
  courses = {}
  total_pages = int(total_pages)+1
  for page in range(1, total_pages):
    if name == 'todos':name = ''
    response = alurasession.get(f'https://cursos.alura.com.br/courses?categoryUrlName={name}&page={page}')
    soup = BeautifulSoup(response.text, 'html.parser')
    total_items = list_items(soup.find_all('li', class_='card-list__item'))
    courses.update(total_items)
  return courses


def get_courses(data_schools):
  selected_course = {}
  for data_school_title, data_school_info in data_schools.items():
    response = alurasession.get(data_school_info['link'])
    soup = BeautifulSoup(response.text, 'html.parser')
    pages = soup.find_all('a', class_='paginationLink')
    pages_total = total_pages(pages)
    print("Cursos disponíveis:")
    courses = pagination(soup, data_school_title, pages_total)
    course_names = list(courses.keys())
    for n, course_name in enumerate(course_names, start=1):
      print(f'{n}. {str(course_name)}')
    choice = int(input("Digite o número do curso que deseja visualizar ou 0 para todos: "))
    if choice == 0:
      print("Todos os cursos selecionados.")
      selected_course[data_school_title] = courses
      return selected_course
    elif 1 <= choice <= len(courses):
      selected_course_name = course_names[choice - 1]
      selected_course[data_school_title] = {selected_course_name: courses[selected_course_name]}
      data_schools[data_school_title][data_school_info['path']] = selected_course
      print(f"Você selecionou: {selected_course_name}")
      return selected_course
 

email, password = credentials()
schools = login(email, password)
data_schools = choose_schools(schools)
courses = get_courses(data_schools)
