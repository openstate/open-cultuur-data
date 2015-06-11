from datetime import datetime
from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

log = get_source_logger('loader')


class ArchiefAlkmaarBaseItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'europeana': 'http://www.europeana.eu/schemas/ese/',
        'dcterms': 'http://purl.org/dc/terms/'
    }

    media_mime_types = {
        'webm': 'video/webm',
        'ogv': 'video/ogg',
        'ogg': 'audio/ogg',
        'mp4': 'video/mp4',
        'm3u8': 'application/x-mpegURL',
        'ts': 'video/MP2T',
        'mpeg': 'video/mpeg',
        'mpg': 'video/mpeg',
        'png': 'image/png',
        'jpg': 'image/jpg',
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(
            xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return self.cleanup_xml_inner(node)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': (
                u'http://www.regionaalarchiefalkmaar.nl/beeldbank/%s/' % (
                    original_id.split(':')[1],)),
            'xml': (
                u'https://maior.memorix.nl/api/oai/raa/key/Bonda/?'
                u'verb=GetRecord&identifier=%s&metadataPrefix=ese' % (
                    original_id,))
        }

    def get_rights(self):
        return u'http://en.wikipedia.org/wiki/Public_domain'

    def cleanup_xml_inner(self, xmlnode):
        cleantext = xmlnode.text.replace("\n", "")
        return unicode(cleantext.strip())

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//dc:title')
        combined_index_data['title'] = title

        descriptions = self.original_item.findall('.//dc:description',
                                                  namespaces=self.namespaces)
        if descriptions is not None:
            if (len(descriptions) > 0):
                combined_index_data['title'] = self.cleanup_xml_inner(
                    descriptions[0])

            if (len(descriptions) > 1):
                combined_index_data['description'] = self.cleanup_xml_inner(
                    descriptions[1])

        date = self._get_text_or_none('.//dc:date')
        if date:
            datesplit = date.split('-')
            if (datesplit[1] == '00') or (datesplit[2] == '00'):
                combined_index_data['date_granularity'] = 4
                combined_index_data['date'] = datetime.strptime(
                    datesplit[0], '%Y')
            else:
                combined_index_data['date_granularity'] = 8
                combined_index_data['date'] = datetime.strptime(
                    date, '%Y-%m-%d')

        authors = self._get_text_or_none('.//dc:creator')
        if authors:
            combined_index_data['authors'] = [authors]

        media = self._get_text_or_none('.//europeana:isShownBy')

        if media:
            combined_index_data['media_urls'] = [{
                'original_url': media,          # always jpg
                'content_type': self.media_mime_types[
                    media.split('.')[-1]].lower()
            }]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # desriptions
        descriptions = self.original_item.findall('.//dc:description',
                                                  namespaces=self.namespaces)
        for description in descriptions:
            text_items.append(self.cleanup_xml_inner(description))

        # Date
        text_items.append(self._get_text_or_none('.//dc:date'))

        # creator
        text_items.append(self._get_text_or_none('.//dc:creator'))

        # Spatial
        text_items.append(self._get_text_or_none('.//dcterms:spatial'))

        # identifier
        text_items.append(self._get_text_or_none('.//dc:identifier'))

        #sets
        header_sets = self.original_item.findall('.//setSpec')

        for header_set in header_sets:
            text_items.append(self.cleanup_xml_inner(header_set))

        log

        return u' '.join([ti for ti in text_items if ti is not None])
