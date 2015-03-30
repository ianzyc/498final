from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from ratemyprofessor.items import ReviewItem
import scrapy
import re

domain = 'http://ratemyprofessors.com'

class RateMyProfessorsSpider(CrawlSpider):
	name = "ratemyprofessor"
	allowed_domains = ["ratemyprofessors.com"]
	start_urls = [
		'http://www.ratemyprofessors.com/search.jsp?query=university+of+michigan'
	]

	def parse_professor(self, response):
		sel = HtmlXPathSelector(response)

		classNames = sel.xpath('//span[@class="name "]/span[@class="response"]/text()').extract()
		reviews = sel.xpath('//td[@class="comments"]/p/text()').extract()
		profName = sel.xpath('//a[@id="areyouquestion"]/text()').extract()
		profName = str(profName)[11:-3]
		
		for i in range(len(classNames)):
			item = ReviewItem() 
			item['profName'] = profName
			item['className'] = re.sub('[0-9_-]*', '', classNames[i]).lower()
			item['review'] = re.sub('\t|\n|\r', '', reviews[i]).lower()
			item['review'] = re.sub('(\s)+', ' ', item['review'])
			yield item

	def parse(self, response):
		for url in HtmlXPathSelector(response).xpath('//li[@class="listing PROFESSOR"]/a/@href').extract():
			 yield scrapy.Request(domain + url, callback=self.parse_professor)

		for url in HtmlXPathSelector(response).xpath('//div[@class="result-pager hidden-md"]/a/@href').extract():
			yield scrapy.Request(domain + url, callback=self.parse)

	def parse_dummy(self, response):
		print 'fuck'


