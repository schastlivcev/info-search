import os
from collections import Counter
import numpy as np
from urllib import parse
from nltk import WordNetLemmatizer
from tokenizer import scan_nltk_packages, tokenize


MAX_NUM_OF_SUITABLE_PAGES = 7
LEMMAS_TF_IDF_DIRECTORY = 'lemmas_tf_idf'
LEMMAS_FILE_NAME = 'lemmas.txt'
INDEX_FILE_NAME = 'index.csv'
INDEX_FILE_DELIMITER = ';'


def preprocess_query(query, lemmas_idf):
    tokenized = tokenize(query)
    lemmatized = Counter(list(map(lambda t: lemmatizer.lemmatize(t), tokenized)))

    query_len = len(tokenized)
    query_tf = dict.fromkeys(lemmatized.keys())
    for lemma in lemmatized:
        query_tf[lemma] = lemmatized[lemma] / query_len

    query_tf_idf = dict.fromkeys(lemmatized.keys())
    for lemma in lemmatized:
        query_tf_idf[lemma] = query_tf[lemma] * lemmas_idf.get(lemma, 0.0)
    return query_tf_idf


def find_suitable_pages(query_tf_idf, lemma_page_scores):
    num_of_pages = len(os.listdir(LEMMAS_TF_IDF_DIRECTORY))
    empty_list = [0.0 for _ in range(num_of_pages)]
    query_matrix = [[0.0 for x in range(len(query_tf_idf))] for y in range(num_of_pages)]
    for word_index, word in enumerate(query_tf_idf.keys()):
        for page in range(num_of_pages):
            query_matrix[page][word_index] = lemma_page_scores.get(word, empty_list)[page]

    query_vector = list(query_tf_idf.values())
    suitability = []
    for page in range(num_of_pages):
        page_vector = query_matrix[page]
        if sum(page_vector) != 0.0:
            suitability.append(cosine_similarity(query_vector, page_vector))
        else:
            suitability.append(0.0)

    suitable_pages = np.argsort(suitability)[::-1]
    suitability.sort(reverse=True)
    return suitability, suitable_pages


def cosine_similarity(a, b):
    cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return cos_sim


if __name__ == '__main__':
    scan_nltk_packages()
    lemmatizer = WordNetLemmatizer()

    print("WikiHow vector search\n"
          f"Type words separated by space.\n"
          "Type '/q' to exit.")

    url_index = []
    with open(INDEX_FILE_NAME, 'r', encoding='utf-8') as index_file:
        for line in index_file.readlines()[1:]:
            values = line.split(INDEX_FILE_DELIMITER)
            url_index.append(values[-1].strip())

    lemmas = set()
    with open(LEMMAS_FILE_NAME, 'r', encoding='utf-8') as lemmas_file:
        for line in lemmas_file.readlines():
            values = line.strip().split(' ')
            lemmas.add(values[0].replace(':', ''))

    lemma_page_scores = {lemma: [] for lemma in lemmas}
    for file in sorted(os.listdir(LEMMAS_TF_IDF_DIRECTORY), key=len):
        with open(f'{LEMMAS_TF_IDF_DIRECTORY}/{file}', 'r', encoding='utf-8') as page:
            for line in page.readlines():
                lemma_page_score = line.split()
                lemma = lemma_page_score[0]
                tf_idf = float(lemma_page_score[-1])
                lemma_page_scores[lemma].append(tf_idf)

    lemmas_idf = dict.fromkeys(lemmas)
    with open(f'{LEMMAS_TF_IDF_DIRECTORY}/{os.listdir(LEMMAS_TF_IDF_DIRECTORY)[0]}', 'r', encoding='utf-8') as page:
        for line in page.readlines():
            lemma_page_score = line.split()
            lemma = lemma_page_score[0]
            idf = float(lemma_page_score[-2])
            lemmas_idf[lemma] = idf

    while True:
        print('Your query: ', end='')
        query = input()
        if query.strip() == '/q':
            break

        query_tf_idf = preprocess_query(query, lemmas_idf)
        # show tf-idf for query
        # print(f'TF-IDF: {query_tf_idf}')

        suitable_page_scores, suitable_pages = find_suitable_pages(query_tf_idf, lemma_page_scores)

        zero_score_index = 0
        for index, score in enumerate(suitable_page_scores):
            if score == 0.0:
                zero_score_index = index
                break

        if zero_score_index == 0:
            print('No suitable pages.')
        else:
            showed_pages = MAX_NUM_OF_SUITABLE_PAGES \
                if (zero_score_index + 1) > MAX_NUM_OF_SUITABLE_PAGES \
                else zero_score_index

            print('Suitable pages: ')
            for i in range(showed_pages):
                print(f'{i + 1}. #{suitable_pages[i] + 1}, '
                      f'URL = https://{parse.quote(url_index[suitable_pages[i]][8:])}, '
                      f'CS = {suitable_page_scores[i]}')