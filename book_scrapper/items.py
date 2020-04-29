# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewItem(scrapy.Item):
    # define the fields for your item here like:

    review_title = scrapy.Field()
    review_author = scrapy.Field()
    review_date = scrapy.Field()
    review_rating = scrapy.Field()
    review_content = scrapy.Field()
    
    pass
