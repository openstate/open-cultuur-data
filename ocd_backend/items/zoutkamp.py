from datetime import datetime

from ocd_backend.items import BaseItem

class ZoutkampItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'xml': 'http://www.w3.org/XML/1998/namespace'
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
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//priref')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': 'http://maritiemdigitaal.nl/index.cfm?event=search.getdetail&id=%s' % original_id,
            'xml': 'http://mmr.adlibhosting.com/madigopacx/wwwopac.ashx?database=ChoiceMardig&search=priref=%s&limit=10&xmltype=unstructured' % original_id
        }

    def get_collection(self):
        return u'Visserijmuseum Zoutkamp'

    def get_rights(self):
        return u'CC-BY'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//title')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//description')
        if description:
            combined_index_data['description'] = description

        authors = self._get_text_or_none('.//creator')
        if authors:
            combined_index_data['authors'] = [authors]

        mediums = self.original_item.findall('.//image',
                                              namespaces=self.namespaces) # always jpg

        if mediums is not None:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium.text,
                    'content_type': self.media_mime_types[medium.text.split('.')[-1]]
                })

        return combined_index_data

    def get_index_data(self):
        invno = self._get_text_or_none('.//invno')
        return {
            'invno': invno
        }

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//title'))

        # Creator
        text_items.append(self._get_text_or_none('.//creator'))

        # Description
        text_items.append(self._get_text_or_none('.//dc:description'))

        # Publisher
        text_items.append(self._get_text_or_none('.//source'))

        return u' '.join([ti for ti in text_items if ti is not None])
