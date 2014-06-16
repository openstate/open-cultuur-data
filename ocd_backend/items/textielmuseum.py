from datetime import datetime

from ocd_backend.items import BaseItem

from ocd_backend.extractors import HttpRequestMixin

class TextielMuseumItem(BaseItem, HttpRequestMixin):
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
        original_urls = {
            'xml': 'http://37.17.215.121:85/opendata/wwwopac.ashx?database=collect&search=priref=%s&xmltype=unstructured' % original_id
        }

        # the object may or may not be available on the textielmuseum website :/
        permalink = 'http://www.textielmuseum.nl/en/collection/%s' % original_id
        resp = self.http_session.head(permalink)
        if resp.status_code >= 200 and resp.status_code < 300:
            original_urls['html'] = permalink

        return original_urls

    def get_collection(self):
        return u'TextielMuseum'

    def get_rights(self):
        return self._get_text_or_none('.//copyright')

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

        date = self._get_text_or_none('.//production.date.start')
        combined_index_data['date'] = None
        combined_index_data['date_granularity'] = 0
        if date:
            combined_index_data['date'] = datetime.strptime(date, '%Y')
            combined_index_data['date_granularity'] = 4

        mediums = None
        id_url = self._get_text_or_none('.//reproduction.identifier_URL')
        if id_url:
            mediums = [
                'http://images.textielmuseum.nl:85/wwwopac.ashx?command=getcontent&server=images&value=%s&width=500&height=500' % id_url
            ]

        if mediums is not None:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium,
                    'content_type': self.media_mime_types[id_url.split('.')[-1]]
                })

        print combined_index_data
        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//title'))

        # Creator
        text_items.append(self._get_text_or_none('.//creator'))

        # Description
        text_items.append(self._get_text_or_none('.//object_name'))

        # Production place
        text_items.append(self._get_text_or_none('.//production.place'))

        # Technique place
        text_items.append(self._get_text_or_none('.//technique'))

        # Material place
        text_items.append(self._get_text_or_none('.//material'))


        return u' '.join([ti for ti in text_items if ti is not None])
