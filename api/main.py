# Send to single device.
from __future__ import print_function

import base64
from email.mime.text import MIMEText

from pymongo import MongoClient

from googleapiclient import errors
from googleapiclient.discovery import build
from httplib2 import Http

from oauth2client import file, client, tools

from pyfcm import FCMNotification
from flask import Flask

app = Flask(__name__)

payload = None

tipoHuella = None

mensaje = None

# Variables del correo a enviar
EMAIL_FROM = 'gomzalo@outlook.com'
EMAIL_TO = 'usaccarlosgrupounoarqui@gmail.com'
EMAIL_SUBJECT = 'Modulo autorización'
EMAIL_CONTENT = ""

#____________________________________Base de datos____________________________________
pymongo = MongoClient()
uri = "mongodb://dbarqui1grupo1:Vvw81LEzH7OSVZUpr2eLXSkIueS6WEvkDzPbr1YTudlpRbLX4dxZKnxAzyZvyFU2rlPKeGLT8WhvvUKmbRSYPQ==@dbarqui1grupo1.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = MongoClient(uri)

db = client.BDnotification
collection = db.Piscina
#____________________________________Notificación a Android____________________________________
def fcmService(tipo):
    push_service = FCMNotification(api_key="AIzaSyCmvxnrqEFD5nwkH_n4RB-ItWLVFsYwCfI")

    if tipo == "1":
        global tipoHuella
        global EMAIL_CONTENT
        tipoHuella = "Acceso correcto, se accedio al hogar"
        EMAIL_CONTENT = tipoHuella
    elif tipo == "0":
        tipoHuella = "Acceso incorrecto, no se accedio al hogar"
        EMAIL_CONTENT = tipoHuella
    elif tipo == "2":
        tipoHuella = "Acceso incorrecto por tercera vez, el sistema se encuentra bloqueado"
        EMAIL_CONTENT = tipoHuella


    #:.........................................................................
    post = {"tipo": "huella",
            "estado": "\""+tipoHuella+"\""
            }
    posts = db.Piscina
    posts.insert_one(post).inserted_id
    #:.........................................................................

    topic_name = "Arqui1"
    message_title = "Modulo autorizacion"
    message_body = str(tipoHuella)
    low_priority = False
    content_available = True

    global payload
    payload = push_service.parse_payload(topic_name=topic_name,message_body=message_body,message_title=message_title,low_priority=low_priority,content_available=content_available)
    push_service.send_request([payload], timeout=4)
    print(payload)
    return tipoHuella

#____________________________________ GMAIL API ____________________________________
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.send'

#Obtener credenciales
def getCred():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    return service


def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error:
      print('An error occurred: %s' % error)

#____________________________________ WEB SERICE ______________________________________________

@app.route("/<num>")
def setNum(num):
    global EMAIL_CONTENT
    global mensaje
    num = num
    fcmService(num)

    service = getCred()
    mensaje = create_message(EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, EMAIL_CONTENT)
    send_message(service,'me', mensaje)

    return str(payload)

if __name__ == '__main__':
    app.run(debug=True)
