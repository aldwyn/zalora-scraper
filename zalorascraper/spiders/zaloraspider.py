import scrapy
import json
import urllib

from zalorascraper.items import ZaloraItem



class ZaloraSpider(scrapy.Spider):
	
	name = 'zalora'
	allowed_domains = ['www.zalora.com.ph']
	start_urls = [
		'http://www.zalora.com.ph/women/',
		'http://www.zalora.com.ph/men/'
	]


	def parse(self, response):
		links = response.css('#sub-menu a::attr("href")')
		for link in links:
			url = response.urljoin(link.extract())
			yield scrapy.Request(url, callback=self.parse_pages)


	def parse_pages(self, response):
		script = response.css('script#seo-template ~ script').extract()[0]
		start = '\'facets\':'
		end = '"is_brunei":false}'
		result = script[script.find(start) + len(start) : script.rfind(end) + len(end)]
		facets = json.loads(result.strip())
		req = {
			'method': 'Costa.ListCatalogProducts',
			'params': [{
				'category_id': facets['category_id'],
				'limit': 48,
				'offset': 0,
				'segment': facets['segment'],
				'dir': facets['dir'],
				'sort': facets['sort'],
				'catalog_type': '',
				'url_key': facets['url_key']
			}]
		}
		start = '"numFound":'
		end = ',"start":0'
		num_found = int(script[script.find(start) + len(start) : script.find(end)])
		for i in xrange(0, num_found, 48):
			req['params'][0]['offset'] = i
			url = response.urljoin('_c/rpc?' + urllib.urlencode({
				'req': json.dumps(req),
				'lang': facets['lang']
			}))
			yield scrapy.Request(url, callback=self.parse_items)


	def parse_items(self, response):
		json_raw = json.loads(response.body_as_unicode())
		for item_json in json_raw['result']['response']['docs']:
			item = ZaloraItem()
			for k in item_json['meta'].keys():
				item[k] = item_json['meta'][k]
			item['link'] = item_json['link']
			item['image'] = item_json['image']
			item['is_new'] = item_json['is_new']
			sizes = [s['size'] for s in item_json['available_sizes']]
			item['available_sizes'] = '|'.join(sizes)
			yield item