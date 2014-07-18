import re
from datetime import datetime

from BeautifulSoup import BeautifulSoup

from ocd_backend.items import BaseItem


class TropenMuseumItem(BaseItem):
    media_mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'tiff': 'image/tiff',
        'tif': 'image/tiff'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    # Get all node values for given path
    def _get_all_or_none(self, xpath_expression):
        node = self.original_item.findall(xpath_expression)
        if node is not None and len(node) > 0:
            items = []
            for item in node:
                items.append(item)
            return items

        return None

    def get_original_object_id(self):
        filename = self._get_text_or_none('.//file/name')
        m = re.search('TMnr (\d+\-?\d+?)\.jpg$', filename)
        if m:
            return m.group(1).decode('utf8')
        else:
            return filename

    def get_description(self):
        text = u''
        description_html = self._get_all_or_none('.//description/language')

        for desc in description_html:
            soup = BeautifulSoup(desc.text)
            filtered_text = soup.find(lang='nl')
            if not filtered_text:
                continue

            filtered_text = filtered_text.findAll(text=True)
            text += u' '.join([unicode(n.string).strip() for n in filtered_text if unicode(n.string) != 'Nederlands:'])

        if text:
            return text

        return None

    def get_original_object_urls(self):
        original_urls = {
            'xml': 'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=%s'
                    %  self._get_text_or_none('.//file/name'),
            'html':  self._get_text_or_none('.//urls/description')
        }

        return original_urls

    def get_rights(self):
        license_url = self._get_text_or_none('.//license_info_url')
        if license_url:
            return license_url
        else:
            return u'http://creativecommons.org/licenses/by-sa/3.0/'

    def get_collection(self):
        return u'Tropenmuseum'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//file/name').split('.')[0]
        combined_index_data['title'] = title
        combined_index_data['description'] = self.get_description()

        date = self._get_text_or_none('.//file/date')
        if date:
            # Date is sometimes wrapped inside html...
            html_date = re.search(r'datetime=\"(.*)\"', date)
            if html_date:
                date = html_date.group(1)

            date_formats = [
                (r'^(\d{4})$', '%Y', 4),
                (r'^(\d{4})-\d{4}$', '%Y', 4),
                (r'^(\d{4}-\d{1,2})$', '%Y-%m', 6),
                (r'^(\d{4}-\d{1,2}-\d{1,2})$', '%Y-%m-%d', 8),
            ]

            for d_regex, d_format, d_granularity in date_formats:
                date_match = re.search(d_regex, date)
                if date_match:
                    combined_index_data['date'] = datetime.strptime(
                        date_match.group(1), d_format)
                    combined_index_data['date_granularity'] = d_granularity

                    # We found a working format, stop trying alternatives
                    break


        img_file_url = self._get_text_or_none('.//urls/file')
        combined_index_data['media_urls'] = [{
          'original_url': img_file_url,
          'content_type': self.media_mime_types[img_file_url.split('.')[-1].lower()]
        }]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # # Title
        title = self._get_text_or_none('.//file/name').split('.')[0]
        text_items.append(title)

        # Categories
        categories = self._get_all_or_none('.//categories/category')
        if categories:
            for category in categories:
                text_items.append(category.text)

        # Description
        text_items.append(self.get_description())

        return u' '.join([ti for ti in text_items if ti is not None])
