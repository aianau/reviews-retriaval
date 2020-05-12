import requests
from bs4 import BeautifulSoup
from flask import Flask, request, Response, render_template
import jsonpickle
import json
import random
from flask_restful import Api, Resource
import re
import goodreads_crawler


app = Flask(__name__)
api = Api(app)


class GoodreadsReview(Resource):
    def get(self):
        goodreads = goodreads_crawler.GoodReads()

        isbn = request.args.get('isbn')  # 9786068965055
        title = request.args.get('title')
        no_of_reviews = 10
        if request.args.get('size') is not None:
            no_of_reviews = int(request.args.get('size'))

        if isbn is not None:
            return goodreads.retrieve_reviews_by_isbn(isbn, no_of_reviews), 200
        elif title is not None:
            return goodreads.retrieve_reviews_by_title(title, no_of_reviews), 200
        else:
            return "Pass arguments", 400


api.add_resource(GoodreadsReview, "/review/goodreads")


class AmazonReview(Resource):
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',

        'Mozilla/5.0 (X11; Linux x86_64) ',
        'AppleWebKit/537.36 (KHTML, like Gecko) ',
        'Chrome/57.0.2987.110 ',
        'Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) ',
        'AppleWebKit/537.36 (KHTML, like Gecko) ',
        'Chrome/61.0.3163.79 ',
        'Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) ',
        'Gecko/20100101 '
    ]

    def get(self):
        title = request.args.get('title')
        url = f'https://www.amazon.com/s?k={title}'
        data = False
        for i in range(1, 40):
            user_agent = random.choice(self.user_agent_list)
            headers = {'User-Agent': user_agent}

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, features="lxml")

            if(soup.find("title", {"dir": "ltr"}) is None):
                # print(user_agent)

                product = soup.find(
                    "div", {"data-component-type": "s-search-result"})
                if(product is not None):
                    product_id = product['data-asin']
                    data = self.getReviews(product_id, user_agent)
                    break

        response_pickled = jsonpickle.encode(data)
        if(data == False):
            return Response(response="failed to find a user agent", status=404, mimetype="application/json")
        return Response(response=response_pickled, status=200, mimetype="application/json")

    def getReviews(self, id, user_agent):
        url = f'https://www.amazon.com/dp/{id}'

        for i in range(1, 100):
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, features="lxml")

            if(soup.find("title", {"dir": "ltr"}) is None):
                ratings = soup.select('.review-rating>span')
                titles = soup.select('.review-title>span')
                authors = soup.select('.a-profile-name')
                dates = soup.select('.review-date')
                review_descriptions = soup.select('.review-text-content>span')
                data = list()
                for i in range(0, len(review_descriptions)):
                    if(str(review_descriptions[i]) != "None"):
                        review = dict({
                            'title': titles[i].text,
                            'author': authors[i].text,
                            'date': dates[i].text,
                            'rating': ratings[i].text,
                            'content': re.sub("<span class=[a-zA-Z- =\"]*>", " ", str(review_descriptions[i]).replace("<br>", " ").replace("<span>", "").replace("</span>", "").replace("<br/>", " "))
                        })
                        data.append(review)

                return data

        return False


api.add_resource(AmazonReview, "/review/amazon")

if __name__ == "__main__":
    app.run()
