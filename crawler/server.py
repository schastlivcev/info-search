import os
from flask import Flask, render_template, request
from vector_searcher import preprocess_query, find_suitable_pages, url_index


PORT = 8080
MIN_SCORE = 0.4
PAGES_DIRECTORY = 'pages'


app = Flask(__name__)


@app.route('/')
def index():
    query = request.values.get('query')
    result = []
    if query is not None:
        query_tf_idf = preprocess_query(query)
        suitable_page_scores, suitable_pages = find_suitable_pages(query_tf_idf)

        for i in range(len(suitable_pages)):
            if suitable_page_scores[i] <= MIN_SCORE:
                break

            with open(PAGES_DIRECTORY + '/'
                      + sorted(os.listdir(PAGES_DIRECTORY), key=len)[suitable_pages[i]], 'r', encoding='utf-8') as page:
                lines = page.readlines()
                res = {'index': i + 1,
                       'page': suitable_pages[i] + 1,
                       'url': url_index[suitable_pages[i]],
                       'cs': suitable_page_scores[i],

                       'name': lines[0],
                       'author': lines[1],
                       'date': lines[2],
                       'preview': lines[3]}

            result.append(res)

    return render_template('search_page.html', query=query, result=result)


if __name__ == "__main__":
    app.run(port=PORT)
