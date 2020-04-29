from flask import Flask, request, Response, render_template
import jsonpickle
import json
import subprocess
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

#integrated scrapy with flask using a subproces
# @app.route('/', methods=['GET'])
# def home():
#     render_template('index.html', title='scraper')


class AmazonReview(Resource):
    def get(self):
        title = request.args.get('title')
        spider_name = "amazon_spider"
        subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', f'title={title}'])
        with open("data_amazon.json") as items_file:
            data = json.load(items_file)

        response_pickled = jsonpickle.encode(data)

        return Response(response=response_pickled, status=200, mimetype="application/json")


api.add_resource(AmazonReview, "/review/amazon")

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=5000)
    
    """
     Use: localhost:5000/review/amazon?title=...(example ?title=altered+carbon)
    """