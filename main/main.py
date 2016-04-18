from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import logging
from google.appengine.api import urlfetch
import json


app = Flask(__name__)
api = Api(app)


FB_PAGE_ACCESS_TOKEN = ""


parser = reqparse.RequestParser()
parser.add_argument('hub.mode')
parser.add_argument('hub.challenge')
parser.add_argument('hub.verify_token')


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


class FbMessengerBotHandler(Resource):
    def get(self):
        args = parser.parse_args()
        if args['hub.verify_token']:
            return int(args['hub.challenge'])
        return 'ok'

    def post(self):
        json = request.get_json()
        logging.debug(json)
        if json:
            fb_messaging = json['entry'][0]['messaging']
            for fb_message in fb_messaging:
                sender = fb_message['sender']
                if 'text' in fb_message['message']:
                    text = fb_message['message']['text']
                    fb_send_text_message(sender, text)

api.add_resource(FbMessengerBotHandler, '/fbmessenger')

if __name__ == '__main__':
    app.run(debug=True)
