import os
import sys
import re
from pprint import pprint
from StringIO import StringIO
from datetime import datetime

import mock
from mock import MagicMock
from nose.tools import raises

import ocd_backend
from ocd_backend.items import StrictMappingDict


_meta_fields = {
    'processing_started': datetime,
    'processing_finished': datetime,
    'source_id': unicode,
    'collection': unicode,
    'rights': unicode,
    'original_object_id': unicode,
    'original_object_urls': dict,
}


def test_strict_mapping_dict_init():
    m = StrictMappingDict(_meta_fields)
    assert m.mapping == _meta_fields


def test_strict_mapping_dict_setitem_ok():
    m = StrictMappingDict(_meta_fields)
    m['source_id'] = u'blaat'
    assert m.store['source_id'] == u'blaat'


@raises(KeyError)
def test_strict_mapping_dict_setitems_faulty_key():
    m = StrictMappingDict(_meta_fields)
    m['source'] = u'blaat'

@raises(TypeError)
def test_strict_mapping_dict_setitems_faulty_value():
    m = StrictMappingDict(_meta_fields)
    m['source_id'] = 'blaat'