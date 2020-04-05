import requests
from bs4 import BeautifulSoup
import json
import time

URL = 'https://www.goodreads.com/api/reviews_widget_iframe'


def retrieve_reviews_by_isbn(isbn, page=1, no_of_pages=1):
    global URL
    params = {'isbn': isbn, 'page': page}
    r = requests.get(url=URL, params=params)

    json_ret = []

    if r.status_code == 200:
        # parse the html response
        soup = BeautifulSoup(r.text, "html.parser")

        # main div with reviews
        div_container = soup.find_all("div", attrs={"class": "gr_review_container"})
        for res in div_container:
            data = {}

            author = res.find("span", attrs={"class": "gr_review_by"}).find("a").text
            data['author'] = author

            date = res.find("span", attrs={"class": "gr_review_date"}).text.strip()
            data['date'] = date

            # get the url for full review
            review_url = res.find("div", attrs={"class": "gr_review_text"}).find("link")['href']

            r = requests.get(url=review_url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")

                rating = soup.find("div", attrs={"class": "rating"}).find("span", attrs={"class": "value-title"})[
                    'title']
                data['rating'] = rating

                description = soup.find("div",
                                        attrs={"class": "reviewText mediumText description readable"}).text.strip()
                data['description'] = description

            # add obtained data to json
            json_ret.append(data)

    if page < no_of_pages:
        json_ret += retrieve_reviews_by_isbn(isbn, page + 1, no_of_pages)

    return json_ret


start_time = time.time()
print('Getting reviews...')
json_content = retrieve_reviews_by_isbn('9786068965055')
print("Running time: %f seconds" % (time.time() - start_time))

# ~15-30 seconds for 10 FULL reviews
# ~2 seconds for 10 partial reviews (300 characters each + ...more link)

with open('data_goodreads.json', 'w') as outfile:
    json.dump(json_content, outfile)
