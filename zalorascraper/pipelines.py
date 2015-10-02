from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):

	def __init__(self):
		self.ids_seen = {}

	def process_item(self, item, spider):
		if item['id_catalog_config'] in self.ids_seen:
			raise DropItem('Duplicate item found: %s' % item)
		else:
			self.ids_seen[item['id_catalog_config']] = None
			return item