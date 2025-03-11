import copy
import logging


class Adapter(logging.LoggerAdapter):

    def __init__(self, logger, extra):
        super(Adapter, self).__init__(logger, extra)
        self.env = extra

    def process(self, msg, kwargs):
        msg, kwargs = super(Adapter, self).process(msg, kwargs)

        result = copy.deepcopy(kwargs)

        default_kwargs_key = ['exc_info', 'stack_info', 'extra']
        custom_key = [k for k in result.keys() if k not in default_kwargs_key]
        result['extra'].update({k: result.pop(k) for k in custom_key})

        return msg, result
