from nltk import WordNetLemmatizer
from tokenizer import scan_nltk_packages


INVERTED_INDEX_FILE_NAME = 'inverted_index.txt'
INDEX_FILE_NAME = 'index.csv'
AND = '&'
OR = '|'
NOT = '-'


if __name__ == '__main__':
    print("WikiHow bool search\n"
          f"Available operations: '{OR}'(or), '{AND}'(and) and '{NOT}'(not) as the first character in the word.\n"
          "Type '/q' to exit.")

    scan_nltk_packages()
    lemmatizer = WordNetLemmatizer()

    num_of_pages = sum(1 for line in open(INDEX_FILE_NAME))  # len(os.listdir(PAGES_DIRECTORY))
    all_pages = set(range(1, num_of_pages))

    index = {}
    with open(INVERTED_INDEX_FILE_NAME) as index_file:
        for line in index_file.readlines():
            lemma_pages = line.split(' ')
            index[lemma_pages[0]] = set(map(int, lemma_pages[1:]))

    while True:
        print('Your query: ', end='')
        query = input().split(' ')
        if query[0] == '/q':
            break

        words = query[::2]
        operators = query[1::2]
        operators.insert(0, OR)

        result = set()
        for word, operator in zip(words, operators):
            if word.startswith(NOT):
                search_word = word[1:]
            else:
                search_word = word

            matched_pages = index.get(lemmatizer.lemmatize(search_word), set())
            if word.startswith(NOT):
                matched_pages = all_pages.difference(matched_pages)
            # show pages for each word
            # print(f'{word}: {sorted(matched_pages)}')

            if operator == OR:
                result.update(matched_pages)
            elif operator == AND:
                result = result.intersection(matched_pages)

        print(f'Suitable pages: {sorted(result)}')
