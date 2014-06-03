import re
from ocd_backend.items import BaseItem
import datetime
from ocd_backend.utils.misc import try_convert, parse_date, parse_date_span

class ErfgoedLeidenBeeldbankItem(BaseItem):
    R_IMG_RES = re.compile(r'http://.+/thumbs/(?P<width>\d+)x(?P<height>\d+)/.+$')

    # Granularities - borrowed from ocd_backend/items/cmutrecht.py

    regexen = [
        ('\?$', (0, lambda _ : None) ),
        ('(\d\d)[\?]+$', (2, lambda (y,) : datetime.datetime(int(y+'00'), 1, 1)) ),
        ('(\d\d\d)\?$', (3, lambda (y,) : datetime.datetime(int(y+'0'), 1, 1)) ),
        ('(\d\d\d\d) ?- ?\d\d\d\d$', (3, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d\d\d0)[\?() ]+$', (3, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        # 'yyyy?' will still have a date granularity of 4
        ('(\d\d\d\d)[\?() ]+$', (4, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d+)$', (4, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d\d\d\d)-(\d+)$', (6, lambda (y,m) : datetime.datetime(int(y), int(m), 1)) ),
        ('(\d\d\d\d)-(\d+)-(\d+)$', (8, lambda (y,m,d) : datetime.datetime(int(y), int(m), int(d))) ),
    ]

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.original_item.nsmap)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def _get_all_text(self, xpath_expression):
        nodes = self.original_item.findall(xpath_expression, namespaces=self.original_item.nsmap)

        texts = []
        for node in nodes:
            if node.text is not None:
                texts.append(unicode(node.text))

        return texts

    def get_original_object_id(self):
        return self._get_text_or_none('.//item/guid').split('/')[-1]

    def get_original_object_urls(self):
        link = self._get_text_or_none('.//item/link')
        if link:
            return {'html': link}

        return {}

    def _get_date_and_granularity(self):

        date = self._get_text_or_none('.//memorix:MEMORIX/field[@name="Datum_afbeelding"]/value')
        if date is not None:
            return parse_date(self.regexen, date)
        else:
            date = self._get_text_or_none('.//item/dcterms:created')
            if date is not None:
                return parse_date(self.regexen, date)
            else:
                date = self._get_text_or_none('.//item/dc:date')
                if date is not None:
                    return parse_date(self.regexen, date)
                else:
                    return None, None

    def get_rights(self):
        return u'Creative Commons Attribution-ShareAlike'

    def get_collection(self):
        return u'Beeldbank Erfgoed Leiden en omstreken'

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


        gran, date = self._get_date_and_granularity()
        if gran and date:
            combined_index_data['date_granularity'] = gran
            combined_index_data['date'] = date

        creators = self.original_item.findall('.//dc:creator',
            namespaces=self.original_item.nsmap)
        if creators is not None:
            authors = []
            for author in creators:
                # Don't add the author if it's unknown to the source ('[onbekend]')
                if author.text == '[onbekend]':
                    continue

                authors.append(unicode(author.text))

            combined_index_data['authors'] = authors

        picture_versions = self.original_item.findall('.//item/ese:isShownBy',
            namespaces=self.original_item.nsmap)
        if picture_versions is not None:
            combined_index_data['media_urls'] = []

            for picture_version in picture_versions:
                # some URL's give an error when requesting, others don't
                # a workaround is to append .jpg to each URL
                # example working: http://neon.pictura-hosting.nl/lei/lei_mrx_bld/thumbs/70x70/lei/00/LEI_REP_8142/PV38162_1I
                # example not working: http://neon.pictura-hosting.nl/lei/lei_mrx_bld/thumbs/188x188/upload/1111/PV22310.1
                url = picture_version.text+'.jpg'
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

        text_items.append(self._get_text_or_none('.//memorix:MEMORIX/field[@name="Annotatie"]/value'))
        text_items.append(self._get_text_or_none('.//memorix:MEMORIX/field[@name="Signatuur"]/value'))
        text_items.append(self._get_text_or_none('.//memorix:MEMORIX/field[@name="Straatnaam"]/value'))
        text_items.append(self._get_text_or_none('.//memorix:MEMORIX/field[@name="Huisnummer"]/value'))

        return u' '.join([ti for ti in text_items if ti is not None])
