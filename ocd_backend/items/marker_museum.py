import hashlib
from datetime import datetime
from pprint import pprint
import re
import os
import urllib

import PIL
import PIL.ExifTags

from ocd_backend.items import BaseItem


class MarkerMuseumItem(BaseItem):
    def get_original_object_id(self):
        m = hashlib.md5()
        m.update(self.original_item['filename'])
        return unicode(m.hexdigest())

    def get_original_object_urls(self):
        return {}

    def get_collection(self):
        return u'Marker Museum'

    def get_rights(self):
        return u'http://creativecommons.org/publicdomain/zero/1.0/deed.nl'

    # this should be factored out to a mixin ....
    def _exif(self):
        img = PIL.Image.open(self.original_item['filename'])
        return {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }

    def get_combined_index_data(self):
        combined_index_data = {}

        try:
            exif = self._exif()
        except AttributeError as e:
            exif = {}

        if exif.has_key('ImageDescription') and exif['ImageDescription']:
            combined_index_data['title'] = exif['ImageDescription']

        if exif.has_key('XPTitle') and exif['XPTitle']:
            combined_index_data['title'] = exif['XPTitle']

        description = os.path.dirname(self.original_item['filename']).replace(
            self.source_definition['path'], '').replace(
                '/', ' '
            ).replace(
                '_', ' '
            )

        combined_index_data['description'] = re.sub(
            r'\d+\.\d+\.\d+', '', description).strip()

        # if we do not have a title, then the description becomes the title
        if 'title' not in combined_index_data:
            combined_index_data['title'] = combined_index_data['description']
            del combined_index_data['description']

        # only use original dates (DateTime exif field is when it was scanned)
        if exif.has_key('DateTimeOriginal') and exif['DateTimeOriginal']:
            try:
                combined_index_data['date'] = datetime.strptime(
                    exif['DateTimeOriginal'].strip(),
                    '%Y-%m-%d %H:%n:%s'
                )
                combined_index_data['date_granularity'] = 14
            except ValueError, e:
                combined_index_data['date'] = None
                combined_index_data['date_granularity'] = 0

        combined_index_data['media_urls'] = [{
            'original_url': '%s%s' % (
                self.source_definition['media_base_url'],
                urllib.quote(self.original_item['filename'].replace(
                    self.source_definition['path'] + '/', ''))),
            'content_type': 'image/jpeg'
        }]

        combined_index_data['all_text'] = self.get_all_text()

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        try:
            exif = self._exif()
        except AttributeError as e:
            exif = {}

        title = u''

        if exif.has_key('ImageDescription') and exif['ImageDescription']:
            title = exif['ImageDescription']

        if exif.has_key('XPTitle') and exif['XPTitle']:
            title = exif['XPTitle']

        description = os.path.dirname(self.original_item['filename']).replace(
            self.source_definition['path'], '').replace(
                '/', ' '
            )

        description = re.sub(
            r'\d+\.\d+\.\d+', '', description).strip()

        text_items = [title, description]

        return u' '.join([ti for ti in text_items if ti is not None])
