import requests


class MailgunApi:

    API_URL = 'https://api.mailgun.net/v3/{}/messages'

    def __init__(self, domain, api_key):
        self.domain = domain
        self.key = api_key
        self.base_url = self.API_URL.format(self.domain)

    def send_email(self, to, subject, text, html=None):

        if not isinstance(to, (list, tuple)):
            to = [to, ]

        data = {
            'from': 'ImageApi <no-reply@{}>'.format(self.domain),
            'to': to,
            'subject': subject,
            'text': text,
            'html': html
        }

        response = requests.post(url=self.base_url,
                                 auth=('api', self.key),
                                 data=data)

        return response


mailgun = MailgunApi(
        domain='sandbox749fb8378fb742fc96c63cac6e8a9262.mailgun.org',
        api_key='503eb1d814399102463dddbebfadcc00-4879ff27-a1ae696c')


