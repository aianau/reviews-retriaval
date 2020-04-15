# -*- coding: utf-8 -*-
import scrapy
from ..items import ReviewItem
import json

class AmazonSpiderSpider(scrapy.Spider):
    name = 'amazon_spider'

    data = {"reviews":[], "success" : True}
    current_callbacks = 0
    total_callbacks = 5

   
    def start_requests(self):
        yield scrapy.Request(f'https://www.amazon.com/s?k={self.title}')
    
    def parse(self, response):
       
        product_id = response.css('.s-result-list').css('div.s-result-item::attr(data-asin)').extract()

        yield response.follow(f'https://www.amazon.com/dp/{product_id[0]}', callback=self.product_parse)
       
    
    def product_parse(self, response):
        items = ReviewItem()
        product_review = response.css('#acrPopover').css('::attr(title)').get()
        self.data['total_product_review'] = product_review
        
        ratings = response.css('.review-rating>span::text').extract()
        titles = response.css('.review-title>span::text').extract()   
        authors = response.css('.a-profile-name::text').extract()
        dates = response.css('.review-date::text').extract() 
        review_descriptions = response.css('.review-text-content>span').extract()
        
        

        for i in range(0, len(ratings)):
            review = dict({
                'title' : titles[i],
                'author' : authors[i],
                'date' : dates[i],
                'rating' : ratings[i],
                'content' : review_descriptions[i].replace("<br>", " ").replace("<span>", "").replace("</span>", "")
            })
            self.data['reviews'].append(review)
        
        if(self.data['reviews'] == [] and self.current_callbacks < self.total_callbacks):
            self.current_callbacks = self.current_callbacks + 1
            self.data['success'] = False
            yield response.follow(f'https://www.amazon.com/s?k={self.title}', callback=self.parse)
        
        # if i want to use item output
        # items['review_title'] = titles
        # items['review_rating'] = ratings
        # items['review_author'] = authors
        # items['review_date'] = dates
        # items['review_content'] = review_descriptions
        # yield items

        with open('data_amazon.json', 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
        
        

