from datetime import timedelta
from email.utils import parsedate_to_datetime
import html2text
from requests_toolbelt.multipart import decoder

from imapclient import IMAPClient
import email
from email.header import decode_header


class IMAPConnection:
    def __init__(self, server, username, password, folder, last_date):
        self.server = server
        self.username = username
        self.password = password
        self.folder = folder
        self.last_date = last_date

    def get_email_body(self, email_message):
        message_content = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True)
                    charset = part.get_content_charset()
                    message_content = body.decode(charset)
                    break
                elif content_type == 'text/html':
                    body = part.get_payload(decode=True)
                    charset = part.get_content_charset()
                    text_maker = html2text.HTML2Text()
                    text_maker.ignore_links = True
                    message_content = text_maker.handle(body.decode(charset))
                    break
        else:
            content_type = email_message.get_content_type()
            if content_type == 'text/plain':
                body = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset()
                message_content = body.decode(charset)
            elif content_type == 'text/html':
                body = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset()
                text_maker = html2text.HTML2Text()
                text_maker.ignore_links = True
                message_content = text_maker.handle(body.decode(charset))
        return message_content

    def get_email_attachments(self, message):
        attachments = []
        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if bool(filename):
                attachment = part.get_payload(decode=True)
                attachments.append((filename, attachment))
        return attachments

    def receive_emails(self):
        server = IMAPClient(self.server)
        server.login(username=self.username, password=self.password)
        server.select_folder(self.folder)
        messages = server.search(['SINCE', self.last_date])
        msgs_numb = len(messages)

        for uid, message_data in server.fetch(messages, "RFC822").items():
            email_message = email.message_from_bytes(message_data[b"RFC822"])
            send_date = parsedate_to_datetime(email_message['date']) if email_message['date'] else None
            attachments = self.get_email_attachments(email_message)

            try:
                subject = decode_header(email_message['subject'])[0][0].decode()
            except:
                subject = ''

            try:
                from_email = str(email_message['from']).split(' ')[-1]
            except:
                from_email = ''

            try:
                body = self.get_email_body(email_message)
            except:
                body = ''

            yield {
                'login': self.username,
                'topic': subject,
                'send_date': send_date,
                'from_email': from_email,
                'message_text': body,
                'attachments': attachments,
                'email_server': self.server,
                'messages_numb': msgs_numb,
            }

