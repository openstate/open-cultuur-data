import re
from datetime import datetime
from pprint import pprint

from ocd_backend.items import BaseItem
from ocd_backend.extractors import HttpRequestMixin

class NationaalArchiefBeeldbankItem(BaseItem, HttpRequestMixin):
    R_IMG_RES = re.compile(
        r'http://.+/thumb/(?P<width>\d+)x(?P<height>\d+)/.+$')

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(
            xpath_expression, namespaces=self.original_item.nsmap)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def _get_all_text(self, xpath_expression):
        nodes = self.original_item.findall(
            xpath_expression, namespaces=self.original_item.nsmap)

        texts = []
        for node in nodes:
            if node.text is not None:
                texts.append(unicode(node.text))

        return texts

    def get_original_object_id(self):
        return self._get_text_or_none('.//item/guid').split('/')[-1]

    def get_original_object_urls(self):
        identifiers = self._get_all_text('.//item//dc:identifier')

        if len(identifiers) > 0:
            link = self._get_text_or_none('.//item/link')
        else:
            link = self._get_text_or_none(
                ('.//item/memorix:MEMORIX//field[@name="PhotoHandle"]'
                '//value[1]')).replace('hdl://', 'http://hdl.handle.net/')

        if link is not None:
            return {'html': link}
        else:
            return {}

    def get_rights(self):
        return u'http://creativecommons.org/licenses/by-sa/3.0/deed.nl'

    def get_collection(self):
        return u'Nationaal Archief'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//item/title')
        if title:
            title = title.replace('\n', ' ').replace('  ', ' ')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//item/description')
        if description:
            description = description.replace('\n', ' ').replace('  ', ' ')

            # Only include the description if it differs from the title
            if description != title:
                combined_index_data['description'] = description

        date = self._get_text_or_none('.//item/dc:date')
        # 0002-11-30T00:00:00Z is used to denote an unknown date
        if date and date != u'0002-11-30T00:00:00Z':
            combined_index_data['date'] = datetime.strptime(
                self._get_text_or_none('.//dc:date'),
                '%Y-%m-%dT%H:%M:%SZ')
        combined_index_data['date_granularity'] = 14

        creators = self.original_item.findall(
            './/dc:creator', namespaces=self.original_item.nsmap)
        if creators is not None:
            authors = []
            for author in creators:
                # Don't add the author if it's unknown to the source
                # ('[onbekend]')
                if author.text == '[onbekend]':
                    continue

                authors.append(unicode(author.text))

            combined_index_data['authors'] = authors

        picture_versions = self.original_item.findall(
            './/item/ese:isShownBy', namespaces=self.original_item.nsmap)
        if picture_versions is not None:
            combined_index_data['media_urls'] = []

            for picture_version in picture_versions:
                url = picture_version.text
                resolution = self.R_IMG_RES.match(url)

                combined_index_data['media_urls'].append({
                    'original_url': url,
                    'content_type': 'image/jpeg',
                    'width': int(resolution.group('width')),
                    'height': int(resolution.group('height'))
                })

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        title = self._get_text_or_none('.//item/title')
        if title:
            title = title.replace('\n', ' ').replace('  ', ' ')
        text_items.append(title)

        description = self._get_text_or_none('.//item/description')
        if description:
            description = description.replace('\n', ' ').replace('  ', ' ')

            # Only include the description if it differs from the title
            if description != title:
                text_items.append(description)

        text_items += self._get_all_text('.//item/dc:subject')
        text_items += self._get_all_text('.//item/dc:creator')
        text_items += self._get_all_text('.//item/dc:coverage')
        text_items += self._get_all_text('.//item/dc:type')
        text_items += self._get_all_text('.//item/dc:identifier')
        text_items += self._get_all_text('.//item/ese:provider')

        text_items.append(self._get_text_or_none(
            './/memorix:MEMORIX/field[@name="Annotatie"]/value'))

        return u' '.join([ti for ti in text_items if ti is not None])
