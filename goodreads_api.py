import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class GoodReads:
    def __init__(self):
        self.URL = 'https://www.goodreads.com/api/reviews_widget_iframe'

    def retrieve_reviews_by_isbn(self, isbn, page=1, no_of_pages=1):
        json_ret = []

        params = {'isbn': isbn, 'page': page}
        r = requests.get(url=self.URL, params=params)

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
            # go recursive for next page
            json_ret += self.retrieve_reviews_by_isbn(isbn, page + 1, no_of_pages)

        return json_ret

    def retrieve_reviews_by_title(self, isbn, page=1, no_of_pages=1):
        return "todo"


class Review(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self):
        goodreads = GoodReads()

        isbn = request.args.get('isbn')  # 9786068965055
        title = request.args.get('title')

        if isbn:
            return goodreads.retrieve_reviews_by_isbn(isbn), 200
        elif title:
            return goodreads.retrieve_reviews_by_isbn(title), 200
        else:
            return "Pass arguments", 400


api.add_resource(Review, "/review")

if __name__ == "__main__":
    # ~15-30 seconds for 10 FULL reviews
    # ~2 seconds for 10 partial reviews (300 characters each + ...more link))

    app.run(debug=True)

    """
     Use: localhost:5000/review?isbn=...
          localhost:5000/review?title=...
    """
