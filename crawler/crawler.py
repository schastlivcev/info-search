import os
import re
import time
import requests
from bs4 import BeautifulSoup


URL = 'https://www.wikihow.com/Special:Randomizer'
NUM_OF_PAGES = 100
PAGES_DIRECTORY = 'pages'
PAGE_PREFIX = 'page_'
INDEX_FILE_NAME = 'index.csv'
INDEX_FILE_DELIMITER = ';'
DELAY_IN_SECONDS = 0
BANNED_WORD_LINES = ['Advertisement', 'Research source', 'X']


def write_page_to_file(file, page):
    soup = BeautifulSoup(page, 'html.parser')
    # named parts
    header = soup.find('div', 'pre-content').h1.text
    content = soup.find('div', 'mw-parser-output')
    author = content.find('a', 'coauthor_link').text
    date = content.find('a', 'byline_info_link').text.strip()
    pre_content = content.find('div', id='intro')
    intro = pre_content.find('div', id='mf-section-0').text.strip()
    # removing unnecessary content
    pre_content.decompose()
    for image_details in content.find_all('div', 'image_details'):
        image_details.decompose()
    for voting in content.find_all('div', re.compile('vote')):
        voting.decompose()
    for downloading in content.find_all('a', re.compile('pdf_link')):
        downloading.decompose()
    related = content.find('div', re.compile('related'))
    if related is not None:
        related.decompose()
    qa = content.find('div', 'qa')
    if qa is not None:
        qa.decompose()
    tip = content.find('div', 'addTipElement')
    if tip is not None:
        tip.decompose()
    # main text
    sections = content.find_all('div', r'section')

    file.write(f'{header}\n')
    file.write(f'{author}\n')
    file.write(f'{date}\n')
    for line in intro.splitlines():
        if is_line_invalid(line):
            continue
        file.write(f'{line.strip()}\n')
    for section in sections:
        for line in section.text.splitlines():
            if is_line_invalid(line):
                continue
            file.write(f'{line.strip()}\n')


def is_line_invalid(line):
    return len(line.strip()) == 0 or line in BANNED_WORD_LINES


if __name__ == '__main__':
    if not os.path.exists(PAGES_DIRECTORY):
        os.mkdir(PAGES_DIRECTORY)

    index_file = open(INDEX_FILE_NAME, 'w', encoding='utf-8')
    index_file.write(f'file_name{INDEX_FILE_DELIMITER}url\n')

    names = []
    i = 0

    while i < NUM_OF_PAGES:
        page = requests.get(URL)
        url = requests.utils.unquote(page.url)
        name = url
        # name = re.sub('[^0-9a-zA-Z]+', '-', url.split('/')[-1])
        # checking if page already exists
        if name in names:
            continue

        names.append(name)
        i += 1

        page_file_name = f'{PAGES_DIRECTORY}/{PAGE_PREFIX}{str(i)}.html'
        with open(page_file_name, 'w', encoding='utf-8') as page_file:
            write_page_to_file(page_file, page.text)

        index_file.write(f'{page_file_name}{INDEX_FILE_DELIMITER}{url}\n')
        time.sleep(DELAY_IN_SECONDS)

    index_file.close()
