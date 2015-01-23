import datetime

from lxml import etree

from ocd_backend.items import BaseItem
from ocd_backend.utils.misc import try_convert, parse_date, parse_date_span


class MuseumRotterdamItem(BaseItem):
    def _get_namespaces(self):
        try:
            return self._namespaces
        except AttributeError, e:
            pass

        default_ns = self.source_definition['default_namespace']
        self._namespaces = self.original_item.nsmap
        self._namespaces[default_ns] = self._namespaces[None]
        del self._namespaces[None]

        return self._namespaces

    def _build_mapping(self):
        try:
            return self._mapping
        except AttributeError, e:
            pass  # we need to build it

        self._mapping = self.source_definition['cb3_mapping']
        return self._mapping

    def _get_field(self, name):
        namespaces = self._get_namespaces()
        mapping = self._build_mapping()
        default_ns = self.source_definition['default_namespace']

        try:
            field_id = mapping[name.lower()]
        except KeyError as e:
            return None

        try:
            xpath_query = './' + default_ns + ':f[@id="' + str(field_id) + '"]'
            res = self.original_item.xpath(
                xpath_query, namespaces=namespaces
            )

            if len(res) > 0:
                return u''.join(res[0].xpath('.//text()'))
            else:
                return None
        except Exception, e:
            return None

    def get_original_object_id(self):
        return unicode(self._get_field('INVENTARISNUMMER'))

    def _get_permalink(self):
        orig_id = self.get_original_object_id()
        extension = self._get_field('EXTENSIE')
        base_url = u'http://museumrotterdam.nl/collectie/item'

        if extension is not None:
            html_link = u'%s/%s-%s' % (
                base_url, orig_id,  extension)
        else:
            html_link = u'%s/%s' % (
                base_url, orig_id)

        return html_link

    def _get_image(self):
        orig_id = self.get_original_object_id()
        extension = self._get_field('EXTENSIE')
        base_url = u'http://museumrotterdam.nl/cache/lowres'

        if extension is not None:
            image_link = u'%s/%s-%s' % (
                base_url, orig_id,  extension)
        else:
            image_link = u'%s/%s' % (
                base_url, orig_id)
        image_link = image_link + u'_1_700_700.jpg'

        return image_link

    def get_original_object_urls(self):
        return {
            'html': self._get_permalink()
        }

    def get_collection(self):
        return u'Museum Rotterdam'

    def get_rights(self):
        # rights are defined for the whole collection.
        return self._get_field('LICENTIE')

    def get_combined_index_data(self):
        index_data = {}

        title = self._get_field('TITEL')
        if title is not None:
            index_data['title'] = unicode(title)

        gran = 4

        try:
            date = datetime.datetime(
                int(self._get_field('DATERING_BEGINJAAR')), 1, 1
            )
        except ValueError as e:
            date = None

        if gran and date:
            index_data['date_granularity'] = gran
            index_data['date'] = date

        description = self._get_field('BESCHRIJVING')
        if description is not None:
            index_data['description'] = unicode(description)

        # author is optional
        index_data['authors'] = []

        # get jpeg images
        index_data['media_urls'] = [{
            'original_url': self._get_image(),
            'content_type': 'image/jpeg'
        }]

        index_data['all_text'] = self.get_all_text()

        return index_data

    def get_index_data(self):
        index_data = {}
        return index_data

    def get_all_text(self):
        return u' '.join([
            self._get_field(item) or u'' for item in [
                'titel', 'objecttrefwoorden', 'plaats_vervaardiging',
                'technieken', 'vervaardiger', 'beschrijving',
                'opschrift_merken', 'trefwoorden', 'associatie',
                'herkomst'
            ]
        ])
