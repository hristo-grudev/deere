import scrapy

from scrapy.loader import ItemLoader
from ..items import DeereItem
from itemloaders.processors import TakeFirst


class DeereSpider(scrapy.Spider):
	name = 'deere'
	start_urls = ['https://www.deere.com/en/our-company/news-and-announcements/news-releases/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news-listings"]/a')
		for post in post_links:
			date = post.xpath('.//h4/text()').get()
			link = post.xpath('./@href').get()
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))
		next_page = response.xpath('//div[@class="pagination-search shown multiple-pages"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="col-sm-12 col-md-12"]//text()[normalize-space()]|(//div[@class="components-container"]/div/div/div/div[@class="content clearfix"])[1]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=DeereItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
