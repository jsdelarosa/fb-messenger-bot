import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world" + "!", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    reply = "Code.Si ha recibido tu mensaje: "+message_text
                    #send an image additionally
                    send_text(sender_id,reply)
                    send_image(sender_id, "https://comlounge.net/wp-content/uploads/2016/02/cropped-Logo_COMlounge.png")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def send_text(recipient_id, text):                                                                                                                                                                             
    """send a text message to a recipient"""
    recipient = { 'id' : recipient_id }
    message = { 'text' : text }
    payload = {
        'recipient' : recipient,
        'message' : message
    }
    send(payload)

def send_image(recipient_id, image_url):
    """send an image to a recipient"""

    recipient = { 'id' : recipient_id }

    # create an image object
    image = { 'url' : image_url }

    # add the image object to an attachment of type "image"
    attachment = {
        'type'      : 'image',
        'payload'   : image
    }

    # add the attachment to a message instead of "text"
    message = { 'attachment' : attachment }

    # now create the final payload with the recipient
    payload = {
        'recipient' : recipient,
        'message' : message
    }
    send(payload)

def send(payload):
    """send a payload via the graph API"""

    headers = {'Content-Type': 'application/json'}
    r = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+os.environ["PAGE_ACCESS_TOKEN"],
        data = json.dumps(payload),
        headers = headers)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
