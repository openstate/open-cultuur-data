def load_object(path):
    """Load an object given it's absolute object path, and return it.

    The object can be a class, function, variable or instance.

    :param path: absolute object path (i.e. 'ocd_backend.extractor.BaseExtractor')
    :type path: str.
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError, "Error loading object '%s': not a full path" % path

    module, name = path[:dot], path[dot+1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise ImportError, "Error loading object '%s': %s" % (path, e)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError, "Module '%s' doesn't define any object named '%s'" % (module, name)

    return obj
