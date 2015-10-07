from scrapy.exceptions import DropItem
from azure.storage.blob import BlobService
import urllib, cStringIO


class DuplicatesPipeline(object):

	def __init__(self):
		self.ids_seen = {}
		self.blob_service = BlobService(
			account_name='zclonestorage',
			account_key='IdZHVSw4QpvFbKzlXuZy5wnDbMlUmalaaYMA0blfWlLd8sexV/uo2yLwt2b9trANmuDFKknThaHQCB3cJAZ2LQ=='
		)

	def process_item(self, item, spider):
		if item['id_catalog_config'] in self.ids_seen:
			raise DropItem('Duplicate item found: %s' % item)
		else:
			self.ids_seen[item['id_catalog_config']] = None
			num = item['link'].split('-')[-1]
			item_id = num[:num.find('.')]
			image_file = cStringIO.StringIO(urllib.urlopen(item['image']).read())
			self.blob_service.put_block_blob_from_file(
				'product-images', item_id, image_file, x_ms_blob_content_type='image/png')
			return item