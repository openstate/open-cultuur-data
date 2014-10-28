from datetime import datetime

from ocd_backend.items import BaseItem

class RijksmuseumItem(BaseItem):
    def get_original_object_id(self):
        return self.original_item['objectNumber']

    def get_original_object_urls(self):
        return {
            'html': 'https://www.rijksmuseum.nl/nl/collectie/%s' % self.get_original_object_id(),
            'json': 'https://www.rijksmuseum.nl/api/nl/collection/%s?format=json' % self.get_original_object_id()
        }

    def get_rights(self):
        return u'Creative Commons Zero'

    def get_collection(self):
        return u'Rijksmuseum'

    def get_combined_index_data(self):
        combined_index_data = {}

        if self.original_item['title']:
            combined_index_data['title'] = self.original_item['title']

        if 'description' in self.original_item and self.original_item['description']:
            combined_index_data['description'] = self.original_item['description']

        if 'dating' in self.original_item and self.original_item['dating']['early']:
            combined_index_data['date'] = datetime.strptime(self.original_item['dating']['early'],
                                                            '%Y-%m-%dT%H:%M:%SZ')
            combined_index_data['date_granularity'] = 14
        elif self.original_item['dating']['year']:
            combined_index_data['date'] = datetime.strptime(str(self.original_item['dating']['year']), '%Y')
            combined_index_data['date_granularity'] = 4

        if self.original_item['principalMakers']:
            authors = []
            for maker in self.original_item['principalMakers']:
                if maker['name'] and maker['name'] not in authors:
                    authors.append(maker['name'])

            if authors:
                combined_index_data['authors'] = authors

        if self.original_item['webImage']:
            combined_index_data['media_urls'] = [
                {
                    'original_url': self.original_item['webImage']['url'],
                    'content_type': 'image/jpeg',
                    'width': self.original_item['webImage']['width'],
                    'height': self.original_item['webImage']['height']
                }
            ]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        if self.original_item['titles']:
            text_items += [t for t in self.original_item['titles'] if t]

        if self.original_item['description']:
            text_items.append(self.original_item['description'])

        if self.original_item['labelText']:
            text_items.append(self.original_item['labelText'])

        if self.original_item['objectTypes']:
            text_items += [t for t in self.original_item['objectTypes'] if t]

        if self.original_item['objectCollection']:
            text_items += [t for t in self.original_item['objectCollection'] if t]

        if self.original_item['makers']:
            for maker in self.original_item['makers']:
                if maker['name']:
                    text_items.append(maker['name'])

                if maker['placeOfBirth']:
                    text_items.append(maker['placeOfBirth'])

                if maker['placeOfDeath']:
                    text_items.append(maker['placeOfDeath'])

                if maker['occupation']:
                    text_items += [t for t in maker['occupation'] if t]

                if maker['roles']:
                    text_items += [t for t in maker['roles'] if t]

                if maker['nationality']:
                    text_items.append(maker['nationality'])

                if maker['biography']:
                    text_items.append(maker['biography'])

                if maker['productionPlaces']:
                    text_items += [t for t in maker['productionPlaces'] if t]

                if maker['schoolStyles']:
                    text_items += [t for t in maker['schoolStyles'] if t]

                if maker['qualification']:
                    text_items.append(maker['qualification'])

        if self.original_item['plaqueDescriptionDutch']:
            text_items.append(self.original_item['plaqueDescriptionDutch'])

        if self.original_item['plaqueDescriptionEnglish']:
            text_items.append(self.original_item['plaqueDescriptionEnglish'])

        if self.original_item['artistRole']:
            text_items.append(self.original_item['artistRole'])

        if self.original_item['acquisition']:
            if self.original_item['acquisition']['method']:
                text_items.append(self.original_item['acquisition']['method'])

            if self.original_item['acquisition']['creditLine']:
                text_items.append(self.original_item['acquisition']['creditLine'])

        if 'exhibitions' in self.original_item:
            for exhibition in self.original_item['exhibitions']:
                if exhibition['title']:
                    text_items.append(exhibition['title'])

                if exhibition['organiser']:
                    text_items.append(exhibition['organiser'])

                if exhibition['place']:
                    text_items.append(exhibition['place'])

        if self.original_item['materials']:
            text_items += [t for t in self.original_item['materials'] if t]

        if self.original_item['techniques']:
            text_items += [t for t in self.original_item['techniques'] if t]

        if self.original_item['productionPlaces']:
            text_items += [t for t in self.original_item['productionPlaces'] if t]

        if self.original_item['objectTypes']:
            text_items += [t for t in self.original_item['objectTypes'] if t]

        return u' '.join(text_items)
