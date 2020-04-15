from flask import Flask, request, Response, render_template
import jsonpickle
import json
import subprocess


app = Flask(__name__)
#integrated scrapy with flask using a subproces
# @app.route('/', methods=['GET'])
# def home():
#     render_template('index.html', title='scraper')


@app.route('/<title>', methods=['GET'])
def get_data(title):
    spider_name = "amazon_spider"
    subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', f'title={title}'])
    with open("data_amazon.json") as items_file:
        data = json.load(items_file)

    
    response_pickled = jsonpickle.encode(data)

    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="127.0.0.1", port=5000)