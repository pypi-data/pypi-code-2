import json

class JsonSettingsProvider(object):
    def load(self, serialized_settings):
        """
        Should return json-like dictionary of settings
        """
        def fix_types(objdict):
            result = {}
            for item in objdict.iteritems():
                result[str(item[0])] = item[1]
            return result
        return json.loads(serialized_settings, object_hook=fix_types)

    def dump(self, settings):
        return json.dumps(settings)
