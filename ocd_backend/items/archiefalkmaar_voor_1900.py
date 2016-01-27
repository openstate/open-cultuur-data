from ocd_backend.items.archiefalkmaar_baseItem import ArchiefAlkmaarBaseItem


class ArchiefAlkmaarVoor1900Item(ArchiefAlkmaarBaseItem):
    def get_collection(self):
        return u'Regionaal Archief Alkmaar Voor 1900'
