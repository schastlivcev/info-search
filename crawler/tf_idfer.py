import os
from collections import Counter
from math import log10
from nltk import WordNetLemmatizer
from tokenizer import tokenize, scan_nltk_packages


TOKENS_TF_IDF_DIRECTORY = 'tokens_tf_idf'
LEMMAS_TF_IDF_DIRECTORY = 'lemmas_tf_idf'
PAGES_DIRECTORY = 'pages'
TOKENS_FILE_NAME = 'tokens.txt'
LEMMAS_FILE_NAME = 'lemmas.txt'
NLTK_PACKAGES = ['tokenizers/punkt', 'corpora/stopwords', 'corpora/wordnet', 'corpora/omw-1.4']


def count_tf(pages, page_counters, corpus):
    pages_tf = []
    for page, page_counter in zip(pages, page_counters):
        page_word_count = len(page)
        page_tf = {}
        for word in corpus:
            page_tf[word] = page_counter[word] / page_word_count
        pages_tf.append(page_tf)
    return pages_tf


def count_idf(pages_count, page_counters, corpus):
    documents_counter = dict.fromkeys(corpus, 0)
    for page_counter in page_counters:
        for word in corpus:
            if page_counter[word] != 0:
                documents_counter[word] += 1

    idf = {}
    for word in corpus:
        idf[word] = log10(pages_count / documents_counter[word])
    return idf


def count_tf_idf(pages_tf, idf, corpus):
    pages_tf_idf = []
    for page_tf in pages_tf:
        page_tf_idf = {}
        for word in corpus:
            page_tf_idf[word] = page_tf[word] * idf[word]
        pages_tf_idf.append(page_tf_idf)
    return pages_tf_idf


def write_tf_idf(pages_tf, idf, pages_tf_idf, corpus, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

    i = 0
    for page_tf, page_tf_idf in zip(pages_tf, pages_tf_idf):
        i += 1
        with open(f'{directory}/page_{i}.txt', 'w', encoding='utf-8') as file:
            for word in corpus:
                file.write(f'{word} {page_tf[word]} {idf[word]} {page_tf_idf[word]}\n')


if __name__ == '__main__':
    scan_nltk_packages()
    lemmatizer = WordNetLemmatizer()

    token_pages = []
    token_page_counters = []
    for file in sorted(os.listdir(PAGES_DIRECTORY), key=len):
        with open(f'{PAGES_DIRECTORY}/{file}', 'r', encoding='utf-8') as page:
            tokens = tokenize(page.read())
            token_pages.append(tokens)
            token_page_counters.append(Counter(tokens))

    tokens = set()
    with open(TOKENS_FILE_NAME, encoding="utf-8") as file:
        for line in file.readlines():
            tokens.add(line.strip())

    token_pages_tf = count_tf(token_pages, token_page_counters, tokens)
    tokens_idf = count_idf(len(token_pages), token_page_counters, tokens)
    token_pages_tf_idf = count_tf_idf(token_pages_tf, tokens_idf, tokens)

    write_tf_idf(token_pages_tf, tokens_idf, token_pages_tf_idf, tokens, TOKENS_TF_IDF_DIRECTORY)

    lemmas = set()
    with open(LEMMAS_FILE_NAME, encoding='utf-8') as lemmas_file:
        for line in lemmas_file.readlines():
            values = line.strip().split(' ')
            lemmas.add(values[0].replace(':', ''))

    lemma_page_counters = []
    for token_page in token_pages:
        lemma_page = list(map(lambda token: lemmatizer.lemmatize(token), token_page))
        lemma_page_counters.append(Counter(lemma_page))

    lemma_pages_tf = count_tf(token_pages, lemma_page_counters, lemmas)
    lemmas_idf = count_idf(len(token_pages), lemma_page_counters, lemmas)
    lemma_pages_tf_idf = count_tf_idf(lemma_pages_tf, lemmas_idf, lemmas)

    write_tf_idf(lemma_pages_tf, lemmas_idf, lemma_pages_tf_idf, lemmas, LEMMAS_TF_IDF_DIRECTORY)