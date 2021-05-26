"""Flask model classes"""
import json

import shortlink.errors

DEFAULT_DOMAIN = "short.est"


class ShortUrl:
    def __init__(self, domain="short.est", long_url=None, title=None,
                 short_url=None):
        self.domain = domain
        self.long_url = long_url
        self.title = title
        self.short_url = short_url

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def build_from_req(req):
        """Create ShortUrl from req: ShortUrl"""
        new_obj = ShortUrl()
        new_obj.domain = req.domain
        new_obj.long_url = req.long_url
        new_obj.title = req.title
        return new_obj
