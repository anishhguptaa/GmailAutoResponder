from __future__ import print_function
import os
import time
import random
import os.path
import datetime
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class vacation:

    def get_new_mails(service, TODAY):
        results = service.users().messages().list(userId='me', q="is:unread after:"+TODAY).execute()
        messages= results.get('messages', [])
        return messages
    
    def reply(service, messages, MSG, From):
        for message in messages:

            Subject=False
            To=False
            MessageID= False
            References=False

            for row in service.users().messages().get(userId='me', id=message['id']).execute()['payload']['headers']:
                if row['name']=='Subject' and not Subject:
                    Subject=row['value']

                if row['name']=='From' and not To:
                    To=row['value']

                if row['name']=='Message-ID' and not MessageID:
                    MessageID=(row['value'])

                if row['name']=='References' and not References:
                    References=(row['value'])

                if To and Subject and MessageID and References:
                    break

            mail = EmailMessage()
            mail.set_content(MSG)
            mail['To'] = To
            mail['From'] = From
            mail['Subject'] = Subject
            mail['In-Reply-To']= MessageID
            mail['References']= MessageID if not References else References 
            mail['threadId'] = message['threadId']

            encoded_message = base64.urlsafe_b64encode(mail.as_bytes()).decode()
            body={'raw': encoded_message,
                'threadId': message['threadId']}
            sent_mail = service.users().messages().send(userId="me", body=body).execute()

            body={"addLabelIds": ['Label_3'],
                "removeLabelIds": ['UNREAD']}

            service.users().threads().modify(userId='me', id=message['threadId'], body=body).execute()


    if __name__=='__main__':

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
         'https://www.googleapis.com/auth/gmail.settings.basic',
         'https://www.googleapis.com/auth/gmail.send',
         'https://www.googleapis.com/auth/gmail.modify']
        
        creds = None
        if os.path.exists(os.getcwd()+'\\\\token.js'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.getcwd()+'\credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            
        except HttpError as error:
            print(f'An error occurred: {error}')


        
        x = datetime.datetime.now()
        TODAY= (x.strftime("%m/%d/%Y"))


        From= service.users().getProfile(userId='me').execute()['emailAddress']


        # name=str(input("Please enter your full name: "))
        Name="Anish Gupta"
        MSG="Hi there,\n\nThank you for your email. I will be out of the office from "+TODAY+" and will not have access to email. If this is urgent, please contact the manager. I will do my best to respond promptly to your email as soon as possible.\n\nBest regards,\n"+Name

        flag=False
        for label in service.users().labels().list(userId='me').execute().get('labels', []):
            if(label['name']=='VACATION'):
                flag=True

        if not flag:
            body={'name': 'VACATION'}
            Label= service.users().labels().create(userId='me', body=body).execute()['id']

        
        while(True):
            messages= get_new_mails(service, TODAY)
            reply(service, messages, MSG, From)
            t= random.randint(44,120)
            time.sleep(t)