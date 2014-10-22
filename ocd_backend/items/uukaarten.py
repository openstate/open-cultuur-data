from lxml import etree
from datetime import datetime
from ocd_backend.extractors import HttpRequestMixin
from ocd_backend.items import BaseItem

class UUKaartenItem(BaseItem, HttpRequestMixin):
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
        """ The image location url needs to be retreived through a 
            separate request. This is done here as at this point
            the required id and url are known.
        """
        obj_id = self.get_original_object_id().split(':')[-1].replace("/","-")

        r = self.http_session.get(self.get_original_object_urls()['xml'])
        r.raise_for_status()

        content = unicode(r.content, 'UTF-8', 'replace')

        parser = etree.XMLParser(recover=True, encoding='utf-8')

        tree = etree.fromstring(content.encode('utf-8'), parser=parser)

        elem = tree.find('.//pageData/page/imgLocation')

        if elem is not None:
            img_loc = elem.text
            return 'http://objects.library.uu.nl/reader/img.php?obj=%s&mode=1&img=%s' % (obj_id, img_loc)
        
        return ''

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id().split(':')[-1]
        return {
            'html': 'http://dspace.library.uu.nl:8080/handle/%s' % original_id,
            'xml': 'http://objects.library.uu.nl/reader/index.php?obj=%s&mode=1' % original_id.replace("/","-")
        }

    def get_rights(self):
        return u'info:eu-repo/semantics/OpenAccess'

    def get_collection(self):
        return u'Universiteit Utrecht Kaarten'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:title')

        combined_index_data['title'] = title

        description = self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:description')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:date')
        if date:
            combined_index_data['date'] = datetime.strptime(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:date'), '%Y')
        combined_index_data['date_granularity'] = 4

        authors = self._get_all_or_none('.//oai:metadata/oai_dc:dc/dc:creator')
        if authors:
            combined_index_data['authors'] = authors

        image_url = self._get_image_link()

        # The image format is reported in the metadata, but the image link always
        # converts it to jpeg format. See ticket #56 and #57
        # mime_type = self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:format')
        # if mime_type is None:
        mime_type = 'image/jpeg'

        combined_index_data['media_urls'] = [{
          'original_url': image_url,
          'content_type': mime_type
        }]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:title'))

        # Creators
        authors = self._get_all_or_none('.//oai:metadata/oai_dc:dc/dc:creator')
        if authors:
            text_items = text_items + authors

        # Subjects
        subjects = self._get_all_or_none('.//oai:metadata/oai_dc:dc/dc:subject')
        if subjects:
            text_items = text_items + subjects

        # Description
        text_items.append(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:description'))

        # Publisher
        text_items.append(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:publisher'))

        # Contributor
        contributors = self._get_all_or_none('.//oai:metadata/oai_dc:dc/dc:contributor')
        if contributors:
            text_items = text_items + contributors

        # Identifier
        text_items.append(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:identifier'))

        # Type
        text_items.append(self._get_text_or_none('.//oai:metadata/oai_dc:dc/dc:type'))

        return u'' #u' '.join([ti for ti in text_items if ti is not None])
