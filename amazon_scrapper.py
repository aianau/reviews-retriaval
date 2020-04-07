import scrapy
import json
from scrapy.crawler import CrawlerProcess

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
            # self.data['title'] = product_title[0]
            # self.data['id'] = product_id[0]
            yield response.follow(f'https://www.amazon.com/dp/{product_id[0]}', callback = self.parse)
        else :
            product_review = response.css('#acrPopover').css('::attr(title)').get()
            self.data['total_product_review'] = product_review

            ratings = response.css('.review-rating>span::text').extract()
            titles = response.css('.review-title>span::text').extract()   
            authors = response.css('.a-profile-name::text').extract()
            dates = response.css('.review-date::text').extract() 
            review_descriptions = response.css('.review-text-content>span::text').extract()
            for i in range(0, len(ratings)):
                review = dict({
                    'title' : titles[i],
                    'author' : authors[i],
                    'date' : dates[i],
                    'rating' : ratings[i],
                    'content' : review_descriptions[i]}
                )
                self.data['reviews'].append(review)

            with open('data_amazon.json', 'w') as json_file:
                json.dump(self.data, json_file, indent=4)
            
            yield{"product_review" : product_review}

# pip install scrapy



if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AmazonSpider, 'Altered+Carbon')
    process.start()