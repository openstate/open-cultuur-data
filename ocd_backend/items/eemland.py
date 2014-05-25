import re
 
from datetime import datetime
from dateutil import parser

from ocd_backend.items import BaseItem


class ArchiefEemlandItem(BaseItem):
    R_IMG_RES = re.compile(r'http://.+/thumb/(?P<width>\d+)x(?P<height>\d+)/.+$')
    
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
        return self._get_text_or_none('.//item/guid')

    def get_original_object_urls(self):
        link = self._get_text_or_none('.//item/link')
        if link:
            return {'html': link}

        return {}

    def get_rights(self):
        return u'CC-0'

    def get_collection(self):
        return u'Regionaal Archief Eemland'

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
        
	if date:
	    #Trying to specify how accurate our date is
            length = len(date)
	    if length == 4:
		granularity = 4	     

	    else:
	        match = re.search('\d{4}-\d{1,2}-\d{1,2}', date)
	        if match:
	            granularity = 8
		
	        else:
		    match = re.search('\d{4}-\d{1,2}', date)
		    
		    if match:
			granularity = 6			

		    else:
		        match = re.search('\d{4}\D{1,5}\d{4}', date)
			
		        if match:
		            granularity = 2
		        else:
			    granularity = 4
	
	    #Try if date string can be parsed, if not extract the first occuring year and extract it from the string
            #This is to work around the occurence of: 1891|1924, 1818-1990, 1990 circa (and others)
	    try:
	       parsed_date = parser.parse(date)
	
	    except:
	       date = re.search('\d{4}', date).group(0)
	       parsed_date = parser.parse(date)

            combined_index_data['date'] = parsed_date
	    combined_index_data['date_granularity'] = granularity

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

        text_items.append(self._get_text_or_none('.//memorix:MEMORIX/field[@name="Annotatie"]/value'))

        return u' '.join([ti for ti in text_items if ti is not None])
