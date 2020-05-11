import requests
from bs4 import BeautifulSoup
from goodreads import client
from goodreads.request import GoodreadsRequestException
from flask import Flask, request, Response, render_template
import jsonpickle
import json
import random
from flask_restful import Api, Resource
import config
import re
app = Flask(__name__)
api = Api(app)


class GoodReads:
    def __init__(self):
        self.KEY = config.api_key
        self.SECRET = config.api_secret

    def retrieve_reviews_by_isbn(self, isbn, no_of_reviews=10):
        # get book's link using GoodReads api
        gc = client.GoodreadsClient(self.KEY, self.SECRET)
        try:
            url = gc.book(isbn=isbn).link
            return self.retrieve_reviews(url, no_of_reviews)
        except GoodreadsRequestException:
            return "Isbn not found!"

    def retrieve_reviews_by_title(self, title, no_of_reviews=10):
        title = title.replace(" ", "+")
        url = 'https://www.goodreads.com/search?q={title}&search_type=books'
        url = url.replace("{title}", title)

        r = requests.get(url=url)
        if r.status_code == 200:
            # parse the html response
            soup = BeautifulSoup(r.text, "html.parser")

            # get the url for book's review
            check_search_result = soup.find(
                "table", attrs={"class": "tableList"})
            if check_search_result is not None:
                review_url = 'https://www.goodreads.com/' + \
                             check_search_result.find("tr").find(
                                 "td").find("a")['href']

                # remove query string from url
                poz = 0
                for ch in review_url:
                    if ch == '?':
                        break
                    poz += 1
                review_url = review_url[0:poz]

                return self.retrieve_reviews(review_url, no_of_reviews)
            else:
                return "Title not found!"

    # noinspection PyMethodMayBeStatic
    def retrieve_reviews(self, url, no_of_reviews):
        json_ret = {}

        r = requests.get(url=url)
        if r.status_code == 200:
            # parse the html response
            soup = BeautifulSoup(r.text, "html.parser")

            overall_rating = soup.find(
                "span", itemprop="ratingValue").text.strip()

            reviews = []
            # main div with review
            main_div = soup.find_all("div", attrs={"class": "left bodycol"})
            for res in main_div:
                author = res.find("span", itemprop="author").find("a")['title']

                date = res.find("a", attrs={"class": "reviewDate"}).text

                check_rating = res.find(
                    "span", attrs={"class": "staticStars notranslate"})
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
                    rating = "Not available"

                check_description = res.find(
                    "div", attrs={"class": "reviewText stacked"})
                if check_description is not None:
                    descriptions = check_description.find(
                        "span").find_all("span")
                    description = descriptions[0].text
                    for desc in descriptions:
                        description = desc.text
                else:
                    description = "Not available"

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


api.add_resource(Review, "/review/goodreads")


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

            response = requests.get(url,headers=headers)
            soup = BeautifulSoup(response.content, features="lxml")

            if(soup.find("title", {"dir":"ltr"}) is None):
                # print(user_agent)
                
                product = soup.find("div", {"data-component-type":"s-search-result"})
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

            if(soup.find("title", {"dir":"ltr"}) is None):
                ratings = soup.select('.review-rating>span')
                titles = soup.select('.review-title>span')  
                authors = soup.select('.a-profile-name')
                dates = soup.select('.review-date')
                review_descriptions = soup.select('.review-text-content>span')
                data = list()
                for i in range(0, len(review_descriptions)):
                    if(str(review_descriptions[i]) != "None"):
                        review = dict({
                            'title' : titles[i].text,
                            'author' : authors[i].text,
                            'date' : dates[i].text,
                            'rating' : ratings[i].text,
                            'content' : re.sub("<span class=[a-zA-Z- =\"]*>", " ",str(review_descriptions[i]).replace("<br>", " ").replace("<span>", "").replace("</span>", "").replace("<br/>", " "))
                        })
                        data.append(review)
            
                return data
            
        return False


api.add_resource(AmazonReview, "/review/amazon")

if __name__ == "__main__":
    app.run(debug=True)

    # import json
    # goodreads = GoodReads()
    # json_content = goodreads.retrieve_reviews_by_title('Harry Potter and the cursed child')
    # with open('data_goodreads.json', 'w') as outfile:
    #     json.dump(json_content, outfile)
