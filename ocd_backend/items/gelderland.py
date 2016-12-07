import re
from datetime import datetime
from flexidate import parse

from ocd_backend.items import BaseItem


class GelderlandItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
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
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(
            xpath_expression,
            namespaces=self.namespaces
        )
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'xml': (
                '%s?verb=GetRecord&identifier=%s&metadataPrefix=%s' % (
                    self.source_definition['oai_base_url'],
                    original_id,
                    self.source_definition['oai_metadata_prefix']
                )
            )
        }

    def get_collection(self):
        return u'Collectie Gelderland'

    def get_rights(self):
        return u'Creative Commons Attribution-ShareAlike'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//oai:title')
        if title:
            combined_index_data['title'] = title

        description = self._get_text_or_none('.//oai:description')
        if description:
            combined_index_data['description'] = description

        date = None
        date_granularity = 0
        # Get date start
        date_start_raw = self._get_text_or_none('.//oai:production.date.start')
        # Skip date if 5 or more digits are concatenated, because we
        # don't know how to parse those numbers
        if date_start_raw:
            if not re.search(r'\d{5}', date_start_raw):
                if re.search(r'\d', date_start_raw):
                    date_start = parse(date_start_raw.strip())

                # Get date end
                date_end_raw = self._get_text_or_none('.//oai:production.date.end')
                if re.search(r'\d', date_end_raw):
                    date_end = parse(date_end_raw.strip())

                # Only save date if something got parsed
                if date_start.isoformat():
                    # Determine granularity
                    date_granularity = len(re.findall(r'\d', date_start.isoformat()))

                    # Take average of start and end date if end date does not
                    # exist and they are not the same
                    if not date_end.isoformat():
                        date = date_start.as_datetime()
                    elif date_start.isoformat() == date_end.isoformat():
                        date = date_start.as_datetime()
                    else:
                        # Take the average of years using integers to also
                        # support before christ years (which datetime doesn't
                        # support)
                        if len(date_start.isoformat()) == 4:
                            average_year = int(date_start.year) + (int(date_end.year) - int(date_start.year)) / 2
                            date = parse(average_year).as_datetime()
                        # Take averages for dates with months and days using
                        # datetime
                        else:
                            date = date_start.as_datetime() + (date_end.as_datetime() - date_start.as_datetime()) / 2

        combined_index_data['date'] = date
        combined_index_data['date_granularity'] = date_granularity

        authors = self._get_text_or_none('.//oai:creator')
        if authors:
            combined_index_data['authors'] = [authors]

        mediums = self.original_item.findall('.//oai:imageUrl', namespaces=self.namespaces)
        if mediums:
            combined_index_data['media_urls'] = []
            for medium in mediums:
                #if medium.text.strip().split('.')[-1].lower() in self.media_mime_types:
                combined_index_data['media_urls'].append(
                    {
                        'original_url': unicode(medium.text.strip()),
                        'content_type': self.media_mime_types[
                            unicode(medium.text).strip().split('.')[-1].lower()
                        ]
                    }
                )

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//oai:title'))

        # Creator
        text_items.append(self._get_text_or_none('.//oai:creator'))

        # Subject
        subjects = self.original_item.findall('.//oai:association.subject', namespaces=self.namespaces)
        for subject in subjects:
            text_items.append(unicode(subject.text))

        # Description
        text_items.append(self._get_text_or_none('.//oai:description'))

        items = self.original_item.findall('.//oai:collection', namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:material', namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:object_category', namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:object_name', namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:production.period', namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        # Publisher
        text_items.append(self._get_text_or_none('.//oai:institution.name'))

        return u' '.join([ti for ti in text_items if ti is not None])
