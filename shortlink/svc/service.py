"""ShortLink BI layer"""
import random
import string

from shortlink.errors import ShortLinkException
from shortlink.model import url


class ShortLinkSvc:
    def __init__(self, token_len):
        self.token_len = token_len
        self.short_urls = {}  # Map of short_url -> ShortUrl obj
        self.long_urls = {}  # Map of long_url -> short_url

    def encode_url(self, short_url_req):
        """Encode a long URL to a short URL """
        if short_url_req.short_url:
            raise ShortLinkException(400, "Invalid request - Please retry "
                                          "without setting short_url field")
        if short_url_req.long_url in self.long_urls:
            raise ShortLinkException(400,
                                     "Invalid request - URL {} is already "
                                     "encoded".format(short_url_req.long_url))
        short_url = url.ShortUrl.build_from_req(short_url_req)

        s_url = None
        # Generate a unique token
        # TODO Handle used up tokens
        while not s_url or s_url in self.short_urls:
            token = ''.join(random.choices(string.ascii_uppercase +
                            string.ascii_lowercase + string.digits,
                            k=self.token_len))
            s_url = "/".join(["http:/", short_url.domain, token])

        short_url.short_url = s_url
        self.short_urls[short_url.short_url] = short_url
        self.long_urls[short_url.long_url] = short_url.short_url
        return short_url

    def decode_url(self, short_url: string):
        """Look up the encoded URL corresponding to short_url"""
        if short_url not in self.short_urls:
            raise ShortLinkException(404,
                                     "short_url {} not found".format(short_url))
        return self.short_urls[short_url]
