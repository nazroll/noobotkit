import json
import logging
import util

from google.appengine.api import urlfetch

from flask import request
from flask_restful import Resource, reqparse

FB_PAGE_ACCESS_TOKEN = ""
FB_WEBHOOK_VERIFY_TOKEN = "abcd1234"

parser = reqparse.RequestParser()
parser.add_argument('hub.mode')
parser.add_argument('hub.challenge')
parser.add_argument('hub.verify_token')


class FbMessengerBotHandler(Resource):
    def get(self):
        args = parser.parse_args()
        logging.debug(args)

        if args['hub.mode'] == 'subscribe':
            if args['hub.verify_token'] == FB_WEBHOOK_VERIFY_TOKEN:
                return int(args['hub.challenge'])
        result = {}
        return util.jsonpify(result)

    def post(self):
        obj = request.get_json()
        logging.debug(json)
        if json:
            fb_messaging = obj['entry'][0]['messaging']
            for fb_message in fb_messaging:
                sender = fb_message['sender']
                if 'text' in fb_message['message']:
                    text = fb_message['message']['text']
                    fb_send_text_message(sender, text)


def fb_send_text_message(sender, text):
    fb_sender_id = sender['id']
    fb_sender_text = text

    reply = {
        'recipient': {
            'id': fb_sender_id
        },
        'message': {
            'text': fb_sender_text
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    payload = json.dumps(reply)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + FB_PAGE_ACCESS_TOKEN
    req = urlfetch.fetch(
        url,
        payload,
        urlfetch.POST,
        headers
    )
    logging.debug(req.content)
