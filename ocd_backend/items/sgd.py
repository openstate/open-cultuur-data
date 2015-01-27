from datetime import datetime

from lxml import etree

from ocd_backend.extractors import HttpRequestMixin
from ocd_backend.items import BaseItem

class SGDItem(BaseItem, HttpRequestMixin):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcx': 'http://krait.kb.nl/coop/tel/handbook/telterms.html',
        'dcterms': 'http://purl.org/dc/terms/',
        'didl': 'urn:mpeg:mpeg21:2002:02-DIDL-NS'
    }

    def _get_text_or_none(self, xpath_expression, tree=None):
        if tree is None:
            tree = self.original_item
        node = tree.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    # Get all node values for given path
    def _get_all_or_none(self, xpath_expression, tree=None):
        if tree is None:
            tree = self.original_item
        node = self.original_item.findall(xpath_expression, namespaces=self.namespaces)
        if node is not None and len(node) > 0:
            items = []
            for item in node:
                items.append(item.text)
            return items

        return None

    def _get_didl_metadata_xml(self, obj_id):
        """ The image location url needs to be retreived through a
            separate request. This is done here as at this point
            the required id and url are known.
        """
        didl_url = 'http://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl' % obj_id
        r = self.http_session.get(didl_url)
        r.raise_for_status()

        content = unicode(r.content, 'UTF-8', 'replace')

        parser = etree.XMLParser(recover=True, encoding='utf-8')

        tree = etree.fromstring(content.encode('utf-8'), parser=parser)

        return tree

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        self.didl_xml = self._get_didl_metadata_xml(original_id)

        try:
            pdf_url = self.didl_xml.xpath(
                './/didl:Component[@dc:identifier="%s:PDF"]/didl:Resource/@ref' % original_id.replace('SGD:', ''),
                namespaces=self.namespaces
            )[0]
        except IndexError, e:
            pdf_url = None

        original_urls = {
            'pdf': pdf_url,
            'xml': 'http://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=dcx' % original_id
        }

        #item_id = self._get_text_or_none('.//didl:Item/didl:Item/@dc:identifier')
        return original_urls

    def get_collection(self):
        return u'Staten Generaal Digitaal'

    def get_rights(self):
        return u'CC0'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//dc:title')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//dc:description')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//dc:date')
        if date:
            try:
                combined_index_data['date'] = datetime.strptime(
                    date.strip(), '%Y-%m-%d'
                )
                combined_index_data['date_granularity'] = 8
            except ValueError:
                pass

        mediums = self.didl_xml.xpath(
            './/didl:Resource[@mimeType="image/jpg"]/@ref',
            namespaces=self.namespaces
        )
        if len(mediums) > 0:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium,
                    'content_type': 'image/jpg'
                })

        return combined_index_data

    def get_index_data(self):
        return {
            'startpage': self._get_text_or_none('.//dcx:startpage'),
            'endpage': self._get_text_or_none('.//dcx:endpage'),
            'type': self._get_text_or_none('.//dc:type'),
            'temporal': self._get_text_or_none('.//dcterms:temporal')
        }

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//dc:title'))

        # Description
        text_items.append(self._get_text_or_none('.//dc:description'))

        # Type
        text_items.append(self._get_text_or_none('.//dc:type'))


        return u' '.join([ti for ti in text_items if ti is not None])
