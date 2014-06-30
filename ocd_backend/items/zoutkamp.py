from ocd_backend.items import BaseItem

class ZoutkampItem(BaseItem):
    def _get_all_text(self, xpath_expression):
        nodes = self.original_item.findall(xpath_expression)

        texts = []
        for node in nodes:
            if node.text is not None:
                texts.append(unicode(node.text))

        return texts

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//priref')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': 'http://maritiemdigitaal.nl/index.cfm?event=search.getdetail&id=%s' % original_id,
            'xml': 'http://mmr.adlibhosting.com/madigopacx/wwwopac.ashx?database=ChoiceMardig&search=priref=%s&xmltype=unstructured' % original_id
        }

    def get_collection(self):
        return u'Visserijmuseum Zoutkamp'

    def get_rights(self):
        return u'CC-BY'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//title')
        combined_index_data['title'] = title

        authors = self._get_all_text('.//creator')
        if authors:
            combined_index_data['authors'] = authors

        mediums = self.original_item.findall('.//image')
        if mediums is not None:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium.text,
                    'content_type': 'image/jpg'
                })

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items += self._get_all_text('.//title')

        # Creator
        text_items = self._get_all_text('.//creator')

        return u' '.join([ti for ti in text_items if ti is not None])
