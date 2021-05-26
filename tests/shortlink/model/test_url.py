from unittest import TestCase

from shortlink.model.url import ShortUrl


class TestShortUrl(TestCase):

    def setUp(self) -> None:
        self.domain = "my.dom"
        self.long_url = "https://loooongg.looongger/something"
        self.short_url = "http://my.dom/Sh0rt"
        self.title = "some title"
        self.target = ShortUrl(domain=self.domain, short_url=self.short_url,
                               long_url=self.long_url, title=self.title)

    def test_init(self):
        self.assertEqual(self.domain, self.target.domain)
        self.assertEqual(self.long_url, self.target.long_url)
        self.assertEqual(self.short_url, self.target.short_url)
        self.assertEqual(self.title, self.target.title)

    def test_to_json(self):
        json_s = self.target.to_json()
        self.assertTrue(self.domain in json_s)
        self.assertTrue(self.long_url in json_s)
        self.assertTrue(self.short_url in json_s)
        self.assertTrue(self.title in json_s)

    def test_build_from_req(self):
        res = ShortUrl.build_from_req(self.target)
        self.assertEqual(res.domain, self.target.domain)
        self.assertEqual(res.long_url, self.target.long_url)
        self.assertEqual(res.title, self.target.title)
        self.assertIsNone(res.short_url)
