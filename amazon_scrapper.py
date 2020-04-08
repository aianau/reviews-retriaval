import scrapy
import json

class AmazonSpider(scrapy.Spider):
    name = 'amazon_search'
    first_page = True
    data = {"reviews":[]}
    def __init__(self, title=None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.amazon.com/s?k={title}']
        self.first_page = True
    

    def parse(self, response):
        if self.first_page == True:

            product_id = response.css('.s-result-list').css('div.s-result-item::attr(data-asin)').extract()
            product_title = response.css('.s-result-list').css('.s-result-list').css('.a-size-medium.a-color-base.a-text-normal').css('::text').extract()

            
            yield{'title':product_title, 'id':product_id}
            self.first_page = False
            self.data['title'] = product_title[0]
            self.data['id'] = product_id[0]
            yield response.follow(f'https://www.amazon.com/dp/{product_id[0]}', callback = self.parse)
        else :
            product_review = response.css('#acrPopover').css('::attr(title)').get()
            self.data['total_product_review'] = product_review
            with open('data_amazon.json', 'w') as json_file:
                json.dump(self.data, json_file)
            # TODO : crawl reviews and add them to data (a review should have a title, author, rating and description)
            yield{"product_review" : product_review}

# pip install scrapy
# scrapy runspider -a title=title+of+searched+book amazon_scrapper.py
# example: scrapy runspider -a title=Altered+Carbon amazon_scrapper.py