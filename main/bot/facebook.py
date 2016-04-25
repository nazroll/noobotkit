import json
import logging
import util
import config

from google.appengine.api import urlfetch

from flask import request
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument('hub.mode')
parser.add_argument('hub.challenge')
parser.add_argument('hub.verify_token')

payload_image = {
    'url': ''
}
payload_template = {
    'template_type': '',
    'elements': [
        {
            'title': '',
            'item_url': '',
            'image_url': '',
            'subtitle': '',
            'buttons': [
                {
                    'type': '',
                    'title': '',
                    'url': '',
                    'payload': ''
                }
            ]
        }
    ]
}
send_message = {
    'recipient': {
        'phone_number': '',
        'id': '',
    },
    'message': {
        'text': '',
        'attachment': {
            'type': '',
            'payload': {},
        }
    },
    'notification_type': ''
}


def set_welcome_message(fb_page_id):
    url = 'https://graph.facebook.com/v2.6/' + fb_page_id + '/thread_settings?access_token=' + config.FACEBOOK_PAGE_ACCESS_TOKEN
    if config.PRODUCTION:
        content = {
            'setting_type': 'call_to_actions',
            'thread_state': 'new_thread',
            'call_to_actions': [
                {
                    'message': {
                        'text': 'Hello there!',
                        'attachment': {
                            'type': 'template',
                            'payload': {
                                'template_type': 'generic',
                                'elements': [
                                    {
                                        'title': 'Welcome to %s' % config.FACEBOOK_BOT_NAME,
                                        'item_url': 'https://gilacoolbot.appspot.com',
                                        'image_url': 'http://messengerdemo.parseapp.com/img/rift.png',
                                        'subtitle': 'This is a subtitle',
                                        'buttons': [
                                            {
                                                'type': 'web_url',
                                                'title': 'View website',
                                                'url': 'https://gilacoolbot.appspot.com'
                                            },
                                            {
                                                'type': 'postback',
                                                'title': 'Start chatting',
                                                'payload': 'DEVELOPER_DEFINED_PAYLOAD',
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        }
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps(content)
        req = urlfetch.fetch(
            url,
            payload,
            urlfetch.POST,
            headers
        )
        logging.debug(req.content)


class SetWelcomeMessage(Resource):
    def get(self):
        set_welcome_message(fb_page_id)


class MainHandler(Resource):
    def get(self):
        args = parser.parse_args()
        logging.debug(args)

        if args['hub.mode'] == 'subscribe':
            if args['hub.verify_token'] == config.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
                return int(args['hub.challenge'])
        result = {}
        return util.jsonpify(result)

    def post(self):
        obj = request.get_json()
        if obj:
            for entry in obj['entry']:
                fb_messaging = entry['messaging']
                fb_page_id = entry['id']
                for fb_obj in fb_messaging:
                    fb_sender = fb_obj['sender']
                    fb_recipient = fb_obj['recipient']

                    if 'message' in fb_obj:
                        fb_content = fb_obj['message']
                        if'attachments' in fb_content:
                            for attachment in fb_content['attachments']:
                                logging.debug('%s %s %s %s "%s"' % (fb_page_id, fb_sender['id'], fb_recipient['id'], attachment['type'], attachment['payload']))
                        else:
                            logging.debug('%s %s %s %s "%s"' % (fb_page_id, fb_sender['id'], fb_recipient['id'], 'text', fb_content))
                    if 'delivery' in fb_obj:
                        fb_delivery = fb_obj['delivery']
                        logging.debug('%s %s %s "%s"' % (fb_page_id, fb_sender['id'], fb_recipient['id'], fb_delivery))

                    # fb_msg_time = fb_message['time']
                    # fb_msg_type = 'text'
                    # fb_msg = ''
                    # fb_msg_text = ''
                    # fb_payload_url = ''
                    #
                    # if 'text' in fb_message['message']:
                    #     fb_msg_text = fb_message['message']['text']
                    #
                    # if 'attachments' in fb_message['message']:
                    #     for attachment in fb_message['message']['attachments']:
                    #         fb_msg_type = attachment['type']
                    #         fb_payload = attachment['payload']
                    #         fb_payload_url = fb_payload['url']
                    # fb_msg = fb_payload_url if fb_payload_url else fb_msg_text
                    #
                    # logging.debug('%s %s %s %s %s "%s"' % (fb_page_id, fb_msg_time, fb_sender['id'], fb_recipient['id'], fb_msg_type, fb_msg))
                    # if fb_msg_type is 'text':
                    #     send_text_message(fb_sender, fb_msg_text)
                    # else:
                    #     send_attachment_message(fb_sender, fb_msg_type, fb_payload)
        result = {}
        return util.jsonpify(result)


def send_attachment_message(sender, attachment_type, payload):
    fb_sender_id = sender['id']
    content = {
        'recipient': {
            'id': fb_sender_id
        },
        'message': {
            'attachment': {
                'type': attachment_type,
                'payload': payload
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps(content)
    logging.debug(payload)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + config.FACEBOOK_PAGE_ACCESS_TOKEN
    if config.PRODUCTION:
        req = urlfetch.fetch(
            url,
            payload,
            urlfetch.POST,
            headers
        )
        logging.debug(req.content)


def send_text_message(sender, text):
    fb_sender_id = sender['id']
    fb_sender_text = text
    content = {
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
    payload = json.dumps(content)
    logging.debug(payload)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + config.FACEBOOK_PAGE_ACCESS_TOKEN
    if config.PRODUCTION:
        req = urlfetch.fetch(
            url,
            payload,
            urlfetch.POST,
            headers
        )
        logging.debug(req.content)
