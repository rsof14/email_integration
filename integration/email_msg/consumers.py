import json
import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from .models import Message
from .email_connection import IMAPConnection
from integration.settings import EMAIL_FOLDER, DEFAULT_DATE


class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'status': 'Connected',
        }))

    @database_sync_to_async
    def get_latest_date(self, server, username):
        item = Message.objects.filter(email_server=server, login=username).order_by(
            '-receive_date').first()
        if item:
            return item.receive_date
        else:
            return datetime.datetime(2024, 1, 1, 0, 0, 0)

    async def disconnect(self, code):
        print("Disconnected")

    @database_sync_to_async
    def save_email(self, login, topic, send_date, from_email, message_text, attachments, email_server):
        msg = Message.objects.create(login=login, topic=topic, send_date=send_date, from_email=from_email,
                                     message_text=message_text, email_server=email_server)
        for filename, attachment in attachments:
            temp_file = NamedTemporaryFile()
            temp_file.write(attachment)
            temp_file.flush()
            msg.attachments.save(filename, File(temp_file))
        return msg

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps({
            'status': 'Fetching Started'
        }))
        data = json.loads(text_data)
        email_server = data["emailServer"]
        login = data["login"]
        password = data["password"]
        latest_date = await self.get_latest_date(email_server, login)
        connection = IMAPConnection(email_server, login, password, EMAIL_FOLDER, latest_date)
        i = 0
        emails_numb = 0
        new_emails = []
        for email in connection.receive_emails():
            i += 1
            emails_numb = email.get('messages_numb')
            await self.send(text_data=json.dumps(
                {
                    'progress_bar':
                        {
                            'messages_numb': emails_numb,
                            'progress': i,
                        },
                    'searching_latest': 'True',
                    'loading_emails': 'False',
                }
            ))
            new_emails.insert(0,
                              await self.save_email(email.get('login'), email.get('topic'), email.get('send_date'),
                                                    email.get('from_email'), email.get('message_text'),
                                                    email.get('attachments'), email.get('email_server')))
            await self.send(text_data=json.dumps({'status': 'Saved in db'}))
        for email in new_emails:
            i -= 1
            await self.send(text_data=json.dumps(
                {
                    'progress_bar':
                        {
                            'messages_numb': emails_numb,
                            'progress': i,
                        },
                    'searching_latest': 'False',
                    'loading_emails': 'True',
                    'email':
                        {
                            'from': email.from_email,
                            'topic': email.topic,
                            'send_date': email.send_date.strftime("%d.%m.%Y %H:%M:%S"),
                            'message': str(email.message_text),
                            'attachments': str(email.attachments),
                        }
                }
            ))
