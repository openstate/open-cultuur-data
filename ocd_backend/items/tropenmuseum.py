import re
import urllib
from lxml import etree
from datetime import datetime
from ocd_backend.extractors import HttpRequestMixin
from ocd_backend.items import BaseItem

class CommonsItem(BaseItem, HttpRequestMixin):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'doc': 'http://www.lyncode.com/xoai',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    # Get all node values for given path
    def _get_all_or_none(self, xpath_expression):
        node = self.original_item.findall(xpath_expression, namespaces=self.namespaces)
        if node is not None and len(node) > 0:
            items = []
            for item in node:
                items.append(item.text)
            return items

        return None

    def _get_image_link(self):
        original_id = self.get_original_object_id()
        if re.match('\d+\-\d+$', original_id):
            return 'http://collectie.tropenmuseum.nl/ImagesHandler.ashx?image=%%5CG%%20schijf%%5CTMSMedia%%5Cimages%%5Cscreen%%5C%s.jpg&width=3078&height=2340' % original_id

    def get_original_object_id(self):
        filename = self._get_text_or_none('.//file/name')
        print filename
        m = re.search('TMnr (\d+\-\d+)\.jpg$', filename)
        if m:
            return m.group(1)
        else:
            return filename

    def get_original_object_urls(self):
        filename = self._get_text_or_none('.//file/name')
        image_link = self._get_image_link()

        original_urls = {
            'xml': 'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=%s&thumbwidth=150&thumbheight=150&versions&meta'% urllib.quote(filename)
        }

        if image_link:
            original_urls['html'] = image_link

        return original_urls

    def get_rights(self):
        license_url = self._get_text_or_none('.//license_info_url')
        if license_url:
            return license_url
        else:
            return u'http://creativecommons.org/licenses/by-sa/3.0/'

    def get_collection(self):
        return u'Tropenmuseum'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//file/name').replace('.jpg', '')

        combined_index_data['title'] = title
        combined_index_data['description'] = title

        date = self._get_text_or_none('.//file/date')
        combined_index_data['date'] = None
        combined_index_data['date_granularity'] = 0
        if date:
            date_match = re.search('datetime\=\"(\d+)\"', date)
            if date_match:
                combined_index_data['date'] = datetime.strptime(
                    date_match.group(1),
                    '%Y'
                )
                combined_index_data['date_granularity'] = 4

        image_url = self._get_image_link()
        if image_url:
            combined_index_data['media_urls'] = [{
              'original_url': image_url,
              'content_type': 'image/jpeg'
            }]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(
            self._get_text_or_none('.//file/name').replace('.jpg', '')
        )

        # Subjects
        subjects = self._get_all_or_none('.//category')
        if subjects:
            text_items = text_items + subjects

        # Identifier
        text_items.append(self.get_original_object_id())

        return u' '.join([ti for ti in text_items if ti is not None])
