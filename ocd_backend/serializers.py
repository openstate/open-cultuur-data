import datetime
import msgpack


def decode_datetime(obj):
    if b'__datetime__' in obj:
        try:
            obj = datetime.datetime.strptime(obj['as_str'], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            obj = datetime.datetime.strptime(obj['as_str'], '%Y-%m-%dT%H:%M:%S')
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.isoformat()}
    return obj


def encoder(obj):
    """
    Encode obj with msgpack, and use custom encoder for datetime objects

    :param obj: value (dict) to encode
    :return: binary document
    """
    return msgpack.packb(obj, default=encode_datetime)


def decoder(obj):
    """
    Reverse of ``encode``; decode objects that was serialized using ``encoder``

    :param obj: binary msgpack
    :return: dict
    """
    return msgpack.unpackb(obj, object_hook=decode_datetime)
