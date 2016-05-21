"""
"""

import unittest

from stackinawsgi.wsgi.request import Request
from stackinawsgi.test.helpers import (
    make_environment
)


class TestWsgiRequest(unittest.TestCase):

    def setUp(self):
        self.environment = make_environment(self)
        self.environment_https = make_environment(self, url_scheme='https')

    def tearDown(self):
        pass

    def test_construction(self):
        self.assertNotIn('QUERY_STRING', self.environment)

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertIsNone(request.query)

    def test_construction_without_path(self):
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['PATH_INFO'] = None

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, '/')
        self.assertIsNone(request.query)

    def test_construction_with_nonroot_path(self):
        self.environment['PATH_INFO'] = u'/happy/days'
        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertIsNone(request.query)

    def test_construction_with_nonroot_path_ends_with_slash(self):
        self.environment['PATH_INFO'] = u'/happy/days/'
        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'][:-1])
        self.assertIsNone(request.query)

    def test_construction_with_qs(self):
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['QUERY_STRING'] = 'happy=days'

        request = Request(self.environment)
        self.assertEqual(request.environment, self.environment)
        self.assertEqual(request.stream, self.environment['wsgi.input'])
        self.assertEqual(request.method, self.environment['REQUEST_METHOD'])
        self.assertEqual(request.path, self.environment['PATH_INFO'])
        self.assertEqual(request.query, self.environment['QUERY_STRING'])

    def test_url_property_http(self):
        self.assertNotIn('QUERY_STRING', self.environment)

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost/"
        )

    def test_url_property_https(self):
        self.assertNotIn('QUERY_STRING', self.environment_https)

        request = Request(self.environment_https)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"https://localhost/"
        )

    def test_url_property_http_alternate_port(self):
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['SERVER_PORT'] = str(8080)

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost:8080/"
        )

    def test_url_property_https_alternate_port(self):
        self.assertNotIn('QUERY_STRING', self.environment_https)
        self.environment_https['SERVER_PORT'] = str(8443)

        request = Request(self.environment_https)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"https://localhost:8443/"
        )

    def test_url_property_with_http_host_envvar(self):
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['HTTP_HOST'] = "stackinabox:9000"

        request = Request(self.environment)
        self.assertIsNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://stackinabox:9000/"
        )

    def test_url_property_http_with_qs(self):
        self.assertNotIn('QUERY_STRING', self.environment)
        self.environment['QUERY_STRING'] = 'happy=days'

        request = Request(self.environment)
        self.assertIsNotNone(request.query)

        url = request.url
        self.assertEqual(
            url,
            u"http://localhost/?happy=days"
        )
