# Send to single device.
from __future__ import print_function

#from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from distutils.command.config import config

from pip._internal.wheel import message_about_scripts_not_on_PATH
from pyfcm import FCMNotification
from flask import Flask
from flask import request


app = Flask(__name__)

payload = None

tipoHuella = None

def fcmService(tipo):
#    global tipoHuella
    push_service = FCMNotification(api_key="AIzaSyCmvxnrqEFD5nwkH_n4RB-ItWLVFsYwCfI")

#    print("tipo: "+str(tipo))

    if tipo == "1":
        global tipoHuella
        tipoHuella = "correcta, se abrio la puerta"
    elif tipo == "0":
        tipoHuella = "incorrecta, no se abrio la puerta"
    elif tipo == "2":
        tipoHuella = "incorrecta por tercera vez, se ha bloqueado el ingreso"


    topic_name = "Arqui1"
    message_title = "Modulo autorizacion"
    message_body = "La huella es " + str(tipoHuella)
    low_priority = False
    content_available = True

    global payload
    payload = push_service.parse_payload(topic_name=topic_name,message_body=message_body,message_title=message_title,low_priority=low_priority,content_available=content_available)
    push_service.send_request([payload], timeout=1)
    print(payload)

#---------------- GMAIL API ---------------------
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def gmailTest():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])


@app.route("/<num>")
def setNum(num):
    num = num
    fcmService(num)
    gmailTest()
    return str(payload)

if __name__ == '__main__':
    app.run(debug=True)
