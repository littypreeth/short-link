import logging
import os
import sys
import time

from flask import Flask, jsonify

from flask_restx import Api, fields, reqparse, Resource

import shortlink.errors
from shortlink.model import url
from shortlink.svc import service

logger = logging.getLogger(__name__)


def setup_logging():
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
    logging.Formatter.converter = time.gmtime
    sysout_h = logging.StreamHandler(sys.stdout)
    sysout_h.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(sysout_h)


def create_app():
    """Create the Flask app and BI service"""
    try:
        setup_logging()
        fapp = Flask(__name__)
        config_module = os.environ.get("SHORTLINK_CONFIG", "shortlink.config")
        fapp.config.from_object(config_module)
        fsvc = service.ShortLinkSvc(int(fapp.config["TOKEN_LEN"]))
        return fapp, fsvc
    except Exception as ex:
        logger.exception("Failed to create ShortLink app")
        raise ex


app, svc = create_app()

# API metadata
api = Api(app, version='1.0', title='ShortLink REST API',
          description='REST API for ShortLink - A cool URL shortening '
                      'service for you.',
          )
api = api.namespace('shortlink', description='URL shortening operations')

# JSON response model
shu_model = api.model('ShortUrl', {
    'domain': fields.String(
        readonly=False,
        required=False,
        description='Domain used for generated URL'),
    'long_url': fields.String(
        readonly=False,
        required=True,
        description='Long URL that is shortened'),
    'title': fields.String(
        readonly=False,
        required=False,
        description='Title for the URL'),
    'short_url': fields.String(
        readonly=True,
        required=True,
        description='The shortened URL that is generated'),
})

# JSON request model
shu_req_parser = reqparse.RequestParser()
shu_req_parser.add_argument(
    'domain', required=False, default=url.DEFAULT_DOMAIN, location='json')
shu_req_parser.add_argument(
    'long_url', required=True, location='json')
shu_req_parser.add_argument(
    'title', required=False, location='json')


@api.route('/encode')
@api.doc(description='Encode a long url to short.')
class ShortUrlEncode(Resource):
        @api.expect(shu_req_parser)
        @api.marshal_with(shu_model)
        def post(self):
            args = shu_req_parser.parse_args()
            req_obj = url.ShortUrl(
                domain=args['domain'],
                long_url=args['long_url'],
                title=args['title']
            )
            logger.debug("%s : %s", type(req_obj), req_obj)
            logger.info("Encode %s", req_obj.long_url)
            sh_url = svc.encode_url(req_obj)
            logger.info("Encoded %s", sh_url.short_url)
            return sh_url


@api.route('/decode/<path:uri>')
@api.doc(description='Decode a short url to original form.')
class ShortUrlDecode(Resource):
    @api.marshal_with(shu_model)
    def get(self, uri):
        in_url = "/".join(["http:/", uri])
        logger.info("Decode URL %s", in_url)
        sh_url = svc.decode_url(in_url)
        logger.info("Decoded URL %s", sh_url)
        return sh_url


@api.errorhandler(shortlink.errors.ShortLinkException)
def handle_exception(err):
    response = {"error": err.error_code, "message": err.msg}
    logger.error(err)
    return response, err.error_code


if __name__ == "__main__":
    app.run()
