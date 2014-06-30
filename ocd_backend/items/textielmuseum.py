from datetime import datetime

from ocd_backend.items import BaseItem

from ocd_backend.extractors import HttpRequestMixin

class TextielMuseumItem(BaseItem, HttpRequestMixin):
    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def _get_all_text(self, xpath_expression):
        nodes = self.original_item.findall(xpath_expression)

        texts = []
        for node in nodes:
            if node.text is not None:
                texts.append(unicode(node.text))

        return texts

    def get_original_object_id(self):
        return self._get_text_or_none('.//priref')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        original_urls = {
            'xml': 'http://37.17.215.121:85/opendata/wwwopac.ashx?database=collect&search=priref=%s&xmltype=unstructured' % original_id
        }

        object_number = self._get_text_or_none('.//object_number')
        if object_number:
            permalink = 'http://www.textielmuseum.nl/en/collection/%s' % object_number

            # Not all objects are published on the website of the Textiel Museum,
            # we perform a HEAD request to find out if the object is available
            resp = self.http_session.head(permalink)
            if resp.status_code == 200:
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

        creators = self.original_item.findall('.//creator')
        if creators is not None:
            authors = []
            for creator in creators:
                if creator not in authors and creator is not "onbekend":
                    authors.append(unicode(creator.text))

            combined_index_data['authors'] = authors

        date = self._get_text_or_none('.//production.date.start')
        if date:
            combined_index_data['date'] = datetime.strptime(date, '%Y')
            combined_index_data['date_granularity'] = 4

        mediums = self.original_item.findall('.//reproduction.identifier_URL')
        if mediums is not None:
            img_url = 'http://images.textielmuseum.nl:85/wwwopac.ashx?command=getcontent&server=images&value=%s'

            combined_index_data['media_urls'] = []
            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': img_url % medium.text,
                    'content_type': 'image/jpg'
                })

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//title'))

        # Creator
        text_items += self._get_all_text('.//creator')

        # Description
        text_items.append(self._get_text_or_none('.//description'))

        # Production place
        text_items += self._get_all_text('.//production.place')

        # Technique
        text_items += self._get_all_text('.//technique')

        # Material
        text_items += self._get_all_text('.//material')

        return u' '.join([ti for ti in text_items if ti is not None])
