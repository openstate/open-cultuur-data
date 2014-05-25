from ocd_backend.utils.misc import load_object

def setup_pipeline(source_definition):
    extractor = load_object(source_definition['extractor'])(source_definition)
    transformer = load_object(source_definition['transformer'])()
    loader = load_object(source_definition['loader'])()

    for item in extractor.run():
	(transformer.s(*item, source_definition=source_definition) | loader.s(source_definition=source_definition)).delay()
