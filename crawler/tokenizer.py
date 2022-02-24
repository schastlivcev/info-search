import os
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords


PAGES_DIRECTORY = 'pages'
TOKENS_FILE_NAME = 'tokens.txt'
LEMMAS_FILE_NAME = 'lemmas.txt'
NLTK_PACKAGES = ['tokenizers/punkt', 'corpora/stopwords', 'corpora/wordnet', 'corpora/omw-1.4']
STOPWORDS = stopwords.words('english')


def scan_nltk_packages():
    for package in NLTK_PACKAGES:
        try:
            nltk.find(package)
        except LookupError:
            nltk.download(package.split('/')[1])


def tokenize(page):
    tokens = nltk.word_tokenize(page)
    lowered_tokens = [token.lower() for token in tokens if token.isalpha()]
    return [token for token in lowered_tokens if token not in STOPWORDS]


def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmas_map = {}
    for token in tokens:
        lemma = lemmatizer.lemmatize(token)
        mapped_tokens = lemmas_map.get(lemma, [])
        mapped_tokens.append(token)
        lemmas_map[lemma] = mapped_tokens
    return lemmas_map


if __name__ == '__main__':
    scan_nltk_packages()

    tokens = set()
    for file in os.listdir(PAGES_DIRECTORY):
        with open(f'{PAGES_DIRECTORY}/{file}', 'r', encoding='utf-8') as page:
            tokens.update(set(tokenize(page.read())))

    print(f'Number of tokens = {len(tokens)}')
    with open(TOKENS_FILE_NAME, 'w', encoding='utf-8') as tokens_file:
        tokens_file.write('\n'.join(tokens))

    lemmas_map = lemmatize(tokens)
    print(f'Number of lemmas = {len(lemmas_map)}')
    with open(LEMMAS_FILE_NAME, 'w', encoding='utf-8') as lemmas_file:
        for lemma, tokens in lemmas_map.items():
            lemmas_file.write(f'{lemma}: {" ".join(tokens)}\n')