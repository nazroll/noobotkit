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


def send_fb_message(payload):
    if config.PRODUCTION:
        try:
            req = urlfetch.fetch(
                'https://graph.facebook.com/v2.6/me/messages?access_token=' + config.FACEBOOK_PAGE_ACCESS_TOKEN,
                payload,
                urlfetch.POST,
                {'Content-Type': 'application/json'}
            )
            logging.debug(req.content)
        except urlfetch.Error as e:
            logging.error(e.message)


def example_message_text(sender, text):
    content = {
        'recipient': {
            'id': sender['id']
        },
        'message': {
            'text': text
        }
    }

    logging.debug('"%s" "%s" "%s"' % (
        'outgoing',
        sender['id'],
        content,
    ))

    payload = json.dumps(content)
    send_fb_message(payload)


def example_message_image(sender, url):
    content = {
        'recipient': {
            'id': sender['id']
        },
        'message': {
            'attachment': {
                'type': 'image',
                'payload': {
                    'url': url
                }
            }
        }
    }

    logging.debug('"%s" "%s" "%s"' % (
        'outgoing',
        sender['id'],
        content,
    ))

    payload = json.dumps(content)
    send_fb_message(payload)


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
                        fb_timestamp = fb_obj['timestamp']
                        fb_mid = fb_content['mid']
                        fb_seq = fb_content['seq']
                        if'attachments' in fb_content:
                            for attachment in fb_content['attachments']:
                                atype = attachment['type']
                                if atype is 'image' or atype is 'video' or atype is 'audio':
                                    logging.debug(
                                        '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (
                                            'incoming',
                                            fb_timestamp,
                                            fb_page_id,
                                            fb_sender['id'],
                                            fb_recipient['id'],
                                            attachment['type'],
                                            attachment['payload']['url'],
                                            fb_seq,
                                            fb_mid
                                        )
                                    )
                                elif atype is 'location':
                                    logging.debug(
                                        '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (
                                            'incoming',
                                            fb_timestamp,
                                            fb_page_id,
                                            fb_sender['id'],
                                            fb_recipient['id'],
                                            attachment['type'],
                                            attachment['payload'],
                                            fb_seq,
                                            fb_mid
                                        )
                                    )
                                else:
                                    logging.debug(
                                        '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (
                                            'incoming',
                                            fb_timestamp,
                                            fb_page_id,
                                            fb_sender['id'],
                                            fb_recipient['id'],
                                            attachment['type'],
                                            attachment['payload'],
                                            fb_seq,
                                            fb_mid
                                        )
                                    )
                        else:
                            logging.debug(
                                '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (
                                    'incoming',
                                    fb_timestamp,
                                    fb_page_id,
                                    fb_sender['id'],
                                    fb_recipient['id'],
                                    'text',
                                    fb_content['text'],
                                    fb_seq,
                                    fb_mid
                                )
                            )
                            if 'show example text' in fb_content['text']:
                                example_message_text(
                                    fb_sender,
                                    'This is an example of a message with text only.'
                                )
                                example_message_text(
                                    fb_sender,
                                    'The last thing you said was: "%s"' % fb_content['text']
                                )
                            if 'show example image' in fb_content['text']:
                                example_message_text(
                                    fb_sender,
                                    'This is an example of a message with an image only.'
                                )
                                example_message_image(
                                    fb_sender,
                                    'http://petersapparel.parseapp.com/img/item100-thumb.png'
                                )

                    elif 'delivery' in fb_obj:
                        fb_delivery = fb_obj['delivery']
                        fb_watermark = fb_delivery['watermark']
                        fb_seq = fb_delivery['seq']
                        if 'mids' in fb_delivery and len(fb_delivery['mids']) > 0:
                            for fb_mid in fb_delivery['mids']:
                                logging.debug(
                                    '"%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (
                                        'delivery',
                                        fb_page_id,
                                        fb_sender['id'],
                                        fb_recipient['id'],
                                        fb_watermark,
                                        fb_seq,
                                        fb_mid
                                    )
                                )
                        else:
                            logging.debug(
                                '"%s" "%s" "%s" "%s" "%s" "%s"' % (
                                    'delivery',
                                    fb_page_id,
                                    fb_sender['id'],
                                    fb_recipient['id'],
                                    fb_watermark,
                                    fb_seq
                                )
                            )
                    else:
                        logging.debug(
                            '"%s" "%s" "%s" "%s" "%s"' % (
                                'incoming',
                                fb_page_id,
                                fb_sender['id'],
                                fb_recipient['id'],
                                fb_obj,
                            )
                        )
        result = {}
        return util.jsonpify(result)
