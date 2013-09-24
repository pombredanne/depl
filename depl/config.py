import os

import yaml


class ValidationError(Exception):
    pass


class Config(object):
    def __init__(self, path, hosts):
        with open(path) as f:
            content = f.read()
        self._cnf = yaml.load(content)
        self.deploy = []

        self._validate()

    def _validate(self):
        if not isinstance(self._cnf, dict):
            ValidationError('Should be a dict')

        with open(os.path.join(os.path.dirname(__file__), 'grammar.yml')) as f:
            grammar = yaml.load(f)
        for key, value in self._cnf.items():
            if key not in grammar:
                raise ValidationError('"%s" is an unkown configuration option'
                                        % key)

            setattr(self, key, self._validate_detail(value, self._cnf[key]))

    def _validate_detail(self, current, grammar):
        result = current
        if isinstance(current, list):
            if not isinstance(grammar, list):
                raise ValidationError("Didn't expect a list in %s" % current)

            list_dict = {}
            for item in grammar:
                if isinstance(item, dict):
                    key, value = item.items()[0]
                    list_dict[key] = value
                else:
                    list_dict[item] = None

            result = []
            for element in current:
                if isinstance(element, dict):
                    if len(element) != 1:
                        raise ValidationError('Dictionary directly in list, %s'
                                              % element)
                    key, value = element.items()[0]
                    if key not in list_dict:
                        raise ValidationError('Key %s not found in grammar'
                                              % key)
                    el = self._validate_detail(value, list_dict[key])
                    result.append(el)
                elif isinstance(element, list):
                    raise ValidationError('List not expected in list %s' % element)
                else:
                    if element not in list_dict:
                        raise ValidationError('Element %s not found in grammar'
                                              % key)
                    result.append(element)
        elif isinstance(current, dict):
            if not isinstance(grammar, dict):
                raise ValidationError("Expected a non-dictionary in %s" % current)

            result = {}
            for key, value in current.items():
                if key not in grammar:
                    raise ValidationError("Key %s is not in grammar." % key)
                result[key] = self._validate_detail(element, grammar[key])
        else:
            # normal type
            if type(grammar) != type(current):
                raise ValidationError("Grammar type doesn't match - %s with %s"
                                      % (grammar, current))
        return result