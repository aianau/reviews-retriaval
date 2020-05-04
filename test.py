import requests
import json
import time


class TestGoodReads:
    def __init__(self):
        self.URL = 'http://stefanbeleuz.pythonanywhere.com/review/goodreads'

    def test_title(self, title, size=10):
        params = {'title': title, 'size': size}

        start_time = time.time()
        r = requests.get(url=self.URL, params=params)
        total_time = time.time() - start_time

        json_string = json.dumps(r.json())
        json_string = json_string[:1] + '"request_time": "' + str(total_time) + '", ' + json_string[1:]

        with open('tests/' + title + '_goodreads.json', 'w') as outfile:
            json.dump(json.loads(json_string), outfile, indent=4)

    def test_isbn(self, isbn, size=10):
        params = {'isbn': isbn, 'size': size}

        start_time = time.time()
        r = requests.get(url=self.URL, params=params)
        total_time = time.time() - start_time

        json_string = json.dumps(r.json())
        json_string = json_string[:1] + '"request_time": "' + str(total_time) + '", ' + json_string[1:]

        with open('tests/' + isbn + '_goodreads.json', 'w') as outfile:
            json.dump(json.loads(json_string), outfile, indent=4)


if __name__ == '__main__':
    test_goodreads = TestGoodReads()

    test_goodreads.test_title('Iona')  # title with default no of reviews
    test_goodreads.test_isbn('9786068965055')  # isbn with default no of reviews
    test_goodreads.test_title('Misery', 5)  # title with no of reviews
    test_goodreads.test_isbn('9788498387568', 2)  # isbn with default no of reviews
    test_goodreads.test_title('Harry Potter')  # uncompleted title
    test_goodreads.test_isbn('123')  # incorrect isbn
    test_goodreads.test_isbn('3786068965055')  # unknown isbn
    test_goodreads.test_title('sadasdd')  # unknown title
