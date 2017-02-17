import scrapy
from hotel_sentiment.items import TripAdvisorReviewItem

#TODO use loaders
#to run this use scrapy crawl tripadvisor_more -a start_url="http://some_url"
#for example, scrapy crawl tripadvisor_more -a start_url="https://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html" -o tripadvisor_new_york.csv -s CLOSESPIDER_ITEMCOUNT=10000
class TripadvisorSpiderMoreinfo(scrapy.Spider):
    name = "tripadvisor_more"

    def __init__(self, *args, **kwargs):
        super(TripadvisorSpiderMoreinfo, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]

    def parse(self, response):
        for href in response.xpath('//div[@class="listing_title"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    def parse_hotel(self, response):
        for href in response.xpath('//div[starts-with(@class,"quote")]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_review)

        next_page = response.xpath('//div[@class="unified pagination "]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_hotel)


    #to get the full review content I open its page, because I don't get the full content on the main page
    #there's probably a better way to do it, requires investigation
    def parse_review(self, response):
        item = TripAdvisorReviewItem()
        #item['title'] = response.xpath('//div[@class="quote"]/text()')[0].extract()[1:-1] #strip the quotes (first and last char)
        #item['content'] = response.xpath('//div[@class="entry"]/p/text()').extract()[0][1:-1]
        item['user_name'] = response.xpath('//div[@class="username mo"]/span[starts-with(@class,"expand_inline scrname")]/text()').extract()[0]
        item['reviewer_location'] = response.xpath('//div[@class="location"]/text()')[0].extract()[1:-1]
        #item['review_stars'] = response.xpath('//span[@class="rate sprite-rating_s rating_s"]/img/@alt').extract()[0][0]

        #item['reviewer_location'] = response.xpath('//div[@class="location"]/text()')[0].extract()[1:-1]

        #item['city'] = response.xpath('//li[starts-with(@class,"breadcrumb_item")]/a/span/text()')[-3].extract()

        #locationcontent = response.xpath('//div[starts-with(@class,"locationContent")]')
        #item['hotel_name'] = locationcontent.xpath('.//div[starts-with(@class,"surContent")]/a/text()')[0].extract()

        #hotelclass = locationcontent.xpath('.//span[starts-with(@class,"star")]/span/img/@alt')
        #if hotelclass:
            #item['hotel_classs'] = hotelclass[0].extract()[0]


        #item['hotel_review_stars'] = locationcontent.xpath('.//div[starts-with(@class,"userRating")]/div/span/img/@alt').extract()[0][0]
        #item['hotel_review_qty'] = locationcontent.xpath('.//div[starts-with(@class,"userRating")]/div/a/text()')[0].extract()

        return item
