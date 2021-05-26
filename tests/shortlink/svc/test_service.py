from unittest import TestCase

from shortlink.errors import ShortLinkException
from shortlink.model.url import ShortUrl
from shortlink.svc.service import ShortLinkSvc


class TestShortLinkSvc(TestCase):

    TOKEN_LEN = 5
    DOMAIN = "my.dom"
    INPUT_URL = "https://loooongg.looongger/something"

    def setUp(self) -> None:
        self.req = ShortUrl(long_url=self.INPUT_URL)
        self.target = ShortLinkSvc(self.TOKEN_LEN)

    def test_encode_url(self):
        ret = self.target.encode_url(self.req)
        self.assertIsNotNone(ret)
        self.assertIsNotNone(ret.short_url)
        self.assertEqual(self.INPUT_URL, ret.long_url)

    def test_encode_url_with_domain(self):
        self.req = ShortUrl(long_url=self.INPUT_URL, domain=self.DOMAIN)
        ret = self.target.encode_url(self.req)
        self.assertIsNotNone(ret)
        self.assertIsNotNone(ret.short_url)
        self.assertEqual(self.INPUT_URL, ret.long_url)
        self.assertTrue(self.DOMAIN in ret.short_url)

    def test_encode_url_existing(self):
        ret = self.target.encode_url(self.req)
        self.assertIsNotNone(ret)
        self.assertRaises(ShortLinkException, self.target.encode_url, self.req)

    def test_encode_url_with_short_url(self):
        req = ShortUrl(long_url=self.INPUT_URL, short_url="something")
        target = ShortLinkSvc(self.TOKEN_LEN)
        self.assertRaises(ShortLinkException, target.encode_url, req)

    def test_decode_url(self):
        ret = self.target.encode_url(self.req)
        self.assertIsNotNone(ret)
        decoded = self.target.decode_url(ret.short_url)
        self.assertIsNotNone(decoded)
        self.assertIsNotNone(decoded.long_url)
        self.assertEqual(self.INPUT_URL, ret.long_url)

    def test_decode_url_with_domain(self):
        self.req = ShortUrl(long_url=self.INPUT_URL, domain=self.DOMAIN)
        ret = self.target.encode_url(self.req)
        self.assertIsNotNone(ret)
        decoded = self.target.decode_url(ret.short_url)
        self.assertIsNotNone(decoded)
        self.assertIsNotNone(decoded.long_url)
        self.assertEqual(self.INPUT_URL, ret.long_url)

    def test_decode_url_not_found(self):
        self.assertRaises(ShortLinkException, self.target.decode_url, "someurl")
