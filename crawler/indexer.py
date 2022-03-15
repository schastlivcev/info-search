import os
from tokenizer import tokenize


PAGES_DIRECTORY = 'pages'
PAGE_PREFIX = 'page_'
LEMMAS_FILE_NAME = 'lemmas.txt'
INVERTED_INDEX_FILE_NAME = 'inverted_index.txt'


def create_inverted_index(lemmas_map):
    inverted_index = {}
    for file in os.listdir(PAGES_DIRECTORY):
        with open(f'{PAGES_DIRECTORY}/{file}', 'r', encoding='utf-8') as page:
            page_content = tokenize(page.read())
            for lemma, tokens in lemmas_map.items():
                for token in tokens:
                    if token in page_content:
                        pages = inverted_index.get(lemma, set())
                        pages.add(file[len(PAGE_PREFIX):file.find('.')])

                        inverted_index[lemma] = pages
    return inverted_index


if __name__ == '__main__':
    lemmas_map = {}
    with open(LEMMAS_FILE_NAME) as lemmas_file:
        for line in lemmas_file.readlines():
            values = line.strip().split(' ')
            lemmas_map[values[0].replace(':', '')] = values[1:]

    inverted_index = create_inverted_index(lemmas_map)
    with open(INVERTED_INDEX_FILE_NAME, 'w', encoding='utf-8') as inverted_index_file:
        for lemma, pages in inverted_index.items():
            inverted_index_file.write(f'{lemma} {" ".join(sorted(pages, key=int))}\n')