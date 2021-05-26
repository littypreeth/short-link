"""
Copyright (c) 2019 Peter Jiping Xie

Courtesy: https://github.com/peterjpxie/REST_API_Test_Framework_Python

Description:
Restful API testing for ShortLink APIs

Install:
pip install -r requirements/test.txt

Run:
pytest

Python version: 3.7 or above

"""

import logging
import string
import unittest
from copy import copy
import random

import requests
import json
import os
import inspect
import sys

if sys.version_info < (3, 7):
    raise Exception("Requires Python 3.7 or above.")

## Parameters
LOG_LEVEL = logging.INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
VALID_HTTP_RESP = (200, 201, 202)

# Assume project structure as below:
# Scripts - python scripts
# Logs - logs
# run.bat - batch script to run

# root_path is parent folder of Scripts folder (one level up)
root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_folder = root_path + os.sep + 'Logs' + os.sep

if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)-7s][ln-%(lineno)-3d]: %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S')


# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name='',
                 formatter=common_formatter):
    """Function setup as many loggers as you want."""
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


# default debug logger
debug_log_filename = log_folder + 'debug.log'
log = setup_logger(debug_log_filename, LOG_LEVEL, 'log')

# logger for API outputs
api_formatter = logging.Formatter('%(asctime)s: %(message)s',
                                  datefmt='%Y-%m-%d %I:%M:%S')
api_outputs_filename = log_folder + 'api_outputs.log'
log_api = setup_logger(api_outputs_filename, LOG_LEVEL, 'log_api',
                       formatter=api_formatter)


def pretty_print_request(request):
    """
    Pretty print Restful request to API log
    argument is request object

    Pay attention at the formatting used in this function because
    it is programmed to be pretty printed and may differ from the
    actual request.
    """
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        request.body)
    )


def pretty_print_response(response):
    """
    Pretty print Restful response to API log
    :param response: HTTP response object
    :return:
    """
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text)
    )


def pretty_print_request_json(request):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        json.dumps(json.loads(request.body), indent=4))
    )


def pretty_print_response_json(response):
    """
    pretty print response in json format.

    If failing to parse body in json format, print in text.
    display body in json format explicitly with expected indent.
    Actually most of the time it is not very necessary because body is formatted
    in pretty print way.

    :param response: HTTP response object
    """
    try:
        resp_data = response.json()
        resp_body = json.dumps(resp_data, indent=4)
    except ValueError:
        # if .json() fails, ValueError is raised, take text format
        resp_body = response.text

    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        resp_body
    ))


class TestAPI(unittest.TestCase):
    """
    Test Restful HTTP API examples. 
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.encode_req = {
            "domain": "my.dom",
            "long_url": "https://somelongurl." +
                        "".join(random.choices(string.ascii_lowercase, k=5)) +
                        ".com",
            "title": "Test URL"
        }
        cls.base_url = "http://localhost:5000/shortlink"
        cls.encode_url = "/".join([cls.base_url, "encode"])
        cls.decode_url = "/".join([cls.base_url, "decode"])

    def test_encode_decode_api(self):
        # Call encode API
        enc_resp = self.post(TestAPI.encode_url,
                         data=json.dumps(TestAPI.encode_req, indent=4),
                         expect_status=200)
        self.verify_response_json(enc_resp, TestAPI.encode_req)

        # Call decode API
        # Get the short uri from url by removing http:// prefix
        decode_url = TestAPI.decode_url + "/" + enc_resp["short_url"][7:]
        de_resp = self.get(decode_url,
                        expect_status=200)
        self.verify_response_json(de_resp, enc_resp)
        self.assertEqual(de_resp["short_url"], enc_resp["short_url"])
        self.assertEqual(de_resp["long_url"], TestAPI.encode_req["long_url"])
        log.info('Test %s passed.' % inspect.stack()[0][3])

    def test_decode_not_found(self):
        decode_url = TestAPI.decode_url + "/not.exist"
        self.get(decode_url, expect_status=404)

    def test_encode_no_long_url(self):
        payload = copy(TestAPI.encode_req)
        del payload["long_url"]
        self.post(TestAPI.encode_url,
                     data=json.dumps(payload, indent=4),
                     expect_status=400)
        log.info('Test %s passed.' % inspect.stack()[0][3])

    def post(self, url, data, headers={},
             verify=False, amend_headers=True, expect_status=0):
        """
        common request post function with below features, which you only need to
        take care of url and body data:
            - append common headers
            - print request and response in API log file
            - arguments are the same as requests.post, except amend_headers.
        
        verify: False - Disable SSL certificate verification 
        """

        # append common headers if none
        if amend_headers:
            if 'Content-Type' not in headers:
                headers['Content-Type'] = r'application/json'
            if 'User-Agent' not in headers:
                headers['User-Agent'] = 'Python Requests'

        # send post request
        resp = requests.post(url, data=data, headers=headers,
                             verify=verify)
        caller_func_name = inspect.stack()[1][3]
        return self.process_response(caller_func_name, resp, expect_status)

    def get(self, url, headers={}, verify=False, expect_status=0):
        """
        common request get function with below features, which you only need to
        take care of url:
            - print request and response in API log file
            - arguments are the same as requests.get
        
        verify: False - Disable SSL certificate verification 
        """
        resp = requests.get(url, headers=headers, verify=verify)
        caller_func_name = inspect.stack()[1][3]
        return self.process_response(caller_func_name, resp, expect_status)

    def process_response(self, caller, resp, expect_status=0):
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)
        if expect_status:
            if resp.status_code != expect_status:
                self.fail("Expected status {}, Actual status {}".format(
                    expect_status, resp.status_code))
        elif resp.status_code not in VALID_HTTP_RESP:
            log.error('%s failed with response code %s.' % (
                caller, resp.status_code))
            self.fail("Request failed {}: {}".format(resp.status_code,
                                                     str(resp.json())))
        return resp.json()

    def verify_response_json(self, body, expected):
        self.assertIsNotNone(body)
        self.assertEqual(body["domain"], expected["domain"])
        self.assertEqual(body["long_url"], expected["long_url"])
        self.assertEqual(body["title"], expected["title"])
        self.assertIsNotNone(body["short_url"])
        self.assertTrue(expected["domain"] in body["short_url"])
