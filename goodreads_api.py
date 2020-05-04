import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_restful import Api, Resource
from goodreads import client
from goodreads.request import GoodreadsRequestException
import config

app = Flask(__name__)
api = Api(app)


class GoodReads:
    def __init__(self):
        self.KEY = config.api_key
        self.SECRET = config.api_secret

    def retrieve_reviews_by_isbn(self, isbn, no_of_reviews=10):
        # isbn is usually 13 characters long (10, before 2007)
        if len(isbn) != 10 and len(isbn) != 13:
            return dict({'error': 'Incorrect isbn!'})

        # get book's link using GoodReads api
        gc = client.GoodreadsClient(self.KEY, self.SECRET)
        try:
            url = gc.book(isbn=isbn).link
            return self.retrieve_reviews(url, no_of_reviews)
        except GoodreadsRequestException:
            return dict({'error': 'Isbn not found!'})

    def retrieve_reviews_by_title(self, title, no_of_reviews=10):
        title = title.replace(' ', '+')
        url = 'https://www.goodreads.com/search?q={title}&search_type=books'
        url = url.replace('{title}', title)

        r = requests.get(url=url)
        if r.status_code == 200:
            # parse the html response
            soup = BeautifulSoup(r.text, 'html.parser')

            check_search_result = soup.find('table', attrs={'class': 'tableList'})
            if check_search_result is not None:
                # check first page of books, for the first one with matching title
                found_books = check_search_result.find_all('tr')
                for found_book in found_books:
                    found_title = found_book.find('td').find('a')['title']
                    if found_title == title:
                        review_url = 'https://www.goodreads.com/' + found_book.find('td').find('a')['href']
                        # remove query string from url
                        index = 0
                        for ch in review_url:
                            if ch == '?':
                                break
                            index += 1
                        review_url = review_url[0:index]

                        return self.retrieve_reviews(review_url, no_of_reviews)

                # if a perfect match is not found, return the first match
                review_url = 'https://www.goodreads.com/' + check_search_result.find('tr').find('td').find('a')['href']
                index = 0
                for ch in review_url:
                    if ch == '?':
                        break
                    index += 1
                review_url = review_url[0:index]

                return self.retrieve_reviews(review_url, no_of_reviews)

            else:
                return dict({'error': 'Title not found!'})

    # noinspection PyMethodMayBeStatic
    def retrieve_reviews(self, url, no_of_reviews):
        json_ret = {}

        r = requests.get(url=url)
        if r.status_code == 200:
            # parse the html response
            soup = BeautifulSoup(r.text, 'html.parser')

            overall_rating = soup.find('span', itemprop='ratingValue').text.strip()

            reviews = []
            # main div with review
            main_div = soup.find_all('div', attrs={'class': 'left bodycol'})
            for res in main_div:
                author = res.find('span', itemprop='author').find('a')['title']

                date = res.find('a', attrs={'class': 'reviewDate'}).text

                check_rating = res.find('span', attrs={'class': 'staticStars notranslate'})
                if check_rating is not None:
                    rating = check_rating['title']
                    if rating == 'it was amazing':
                        rating = 5
                    elif rating == 'really liked it':
                        rating = 4
                    elif rating == 'liked it':
                        rating = 3
                    elif rating == 'it was ok':
                        rating = 2
                    else:
                        rating = 1
                else:
                    rating = 'Not available'

                check_description = res.find('div', attrs={'class': 'reviewText stacked'})
                if check_description is not None:
                    descriptions = check_description.find('span').find_all('span')
                    description = descriptions[0].text
                    for desc in descriptions:
                        description = desc.text
                else:
                    description = 'Not available'

                review = dict({
                    'author': author,
                    'date': date,
                    'rating': rating,
                    'description': description
                })

                reviews.append(review)

                if len(reviews) == no_of_reviews:
                    break

            # add obtained data to json
            json_ret = dict({
                'overall_rating': overall_rating,
                'reviews': reviews
            })

        return json_ret


class Review(Resource):
    # noinspection PyMethodMayBeStatic
    def get(self):
        goodreads = GoodReads()

        isbn = request.args.get('isbn')
        title = request.args.get('title')
        no_of_reviews = 10
        if request.args.get('size') is not None:
            no_of_reviews = int(request.args.get('size'))

        if isbn is not None:
            return goodreads.retrieve_reviews_by_isbn(isbn, no_of_reviews), 200
        elif title is not None:
            return goodreads.retrieve_reviews_by_title(title, no_of_reviews), 200
        else:
            return 400


api.add_resource(Review, '/review/goodreads')

if __name__ == '__main__':
    app.run(debug=True)
