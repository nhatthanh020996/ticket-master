import abc
import sendgrid
from sendgrid.helpers.mail import (
    Mail, Email, To, CustomArg, Personalization, MailSettings, SandBoxMode,
    Substitution, From
)

from settings import settings

class IEmailProviderService(abc.ABC):
    @abc.abstractmethod
    def send_with_template_id(self, data):
        raise NotImplementedError(
            "The function have to implement in the concrete class"
        )

    @abc.abstractmethod
    def send_with_template(self, data):
        raise NotImplementedError(
            "The function have to implement in the concrete class"
        )
    
    @abc.abstractmethod
    def register_template(self, name, subject, content, is_html) -> str:
        raise NotImplementedError(
            "The function have to implement in the concrete class"
        )
    
    @abc.abstractmethod
    def send_with_template(self, data: dict, content: str = None, html_content: str = None):
        raise NotImplementedError(
            "The function have to implement in the concrete class"
        )
    
    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError(
            "The function have to implement in the concrete class"
        )



    
class SendgridEmailProviderService(IEmailProviderService):
    def __init__(self, credentials: str = None):
        self._credentials = credentials
        self._client = sendgrid.SendGridAPIClient(api_key=self._credentials['api_key'])

    def send_with_template_id(self, data, template_id):
        """
        data = {
            "from_email": {
                "email_address": "sender@example.com",
                "email_name": "sender"
            },
            "subject": "",
            "is_sandbox_mode": True,
            "is_multiple": True,
            'template_id': '90630358-67fa-4b62-84ac-1bec2e5b8270',
            "destination": {
                "email": "receipent1@example.com",
                "name": "receipent1",
                "dynamic_data": {},
                'cc': ['someone20@example.com', 'someone21@example.com'],
                'bcc': [],
            }
            "destinations": [
                {
                    "email": "receipent1@example.com",
                    "name": "receipent1"
                    'cc': ['someone20@example.com', 'someone21@example.com'],
                    'bcc': [],
                    'subject': None,
                    'dynamic_data': {},
                },
                {
                    "email": "receipent2@example.com",
                    "name": "receipent2"
                    'cc': ['someone1@example.com', 'someone2@example.com'],
                    'bcc': [],
                    'subject': None,
                    'dynamic_data': {},
                }
            ]
        }
        """
        from_email = data['payload']['sender']
        subject = data['payload']['subject']
        destination = data['payload']['destination']

        mail = Mail(from_email=from_email, is_multiple=(data['type'] == 'BULK'))
        mail.template_id = template_id
        mail.subject = subject
        mail.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=data['is_sandbox_mode']))
        
        if data['type'] == 'SINGLE':
            personalization = Personalization()
            to = To(email=destination['email'], name=destination['name'], dynamic_template_data=destination['dynamic_data'])
            personalization.add_to(to)
            personalization.ccs = [Email(email=recipient) for recipient in destination['cc'] or []]
            personalization.bccs = [Email(email=recipient) for recipient in destination['bcc'] or []]
            mail.add_personalization(personalization)
        
        else:
            for destination in data['payload']['destinations']:
                email = destination.get('email')
                dynamic_template_data = destination.get('dynamic_data', {})
                personalization = Personalization()
                to_email = To(email=email, dynamic_template_data=dynamic_template_data)
                personalization.add_to(to_email)
                personalization.ccs = [Email(email=recipient) for recipient in destination['cc'] or []]
                personalization.bccs = [Email(email=recipient) for recipient in destination['bcc'] or []]
                personalization.subject = destination['subject'] if destination['subject'] is not None else subject
                mail.add_personalization(personalization)
            
        self._client.send(mail)


    def send_with_template(self, data: dict, content: str = None, html_content: str = None):
        """
        data = {
            "from_email": {
                "email_address": "sender@example.com",
                "email_name": "sender"
            },
            "is_sandbox_mode": True,
            "subject": "",
            "is_multiple": True,
            "destination": {
                "email": "receipent1@example.com",
                "name": "receipent1",
                "dynamic_data": {},
                'cc': ['someone20@example.com', 'someone21@example.com'],
                'bcc': [],
            }
            "destinations": [
                {
                    "email": "receipent1@example.com",
                    "name": "receipent1"
                    'cc': ['someone20@example.com', 'someone21@example.com'],
                    'bcc': [],
                    'subject': None,
                    'dynamic_data': {},
                },
                {
                    "email": "receipent2@example.com",
                    "name": "receipent2"
                    'cc': ['someone1@example.com', 'someone2@example.com'],
                    'bcc': [],
                    'subject': None,
                    'dynamic_data': {},
                }
            ]
        }
        """
        email_address = data['payload']['sender']
        email_name = data['payload']['brand']['name']
        from_email = From(email=email_address, name=email_name)
        
        subject = data['payload']['subject']
        destination = data['payload']['destination']

        mail = Mail(from_email=from_email, is_multiple=(data['type'] == 'BULK'), plain_text_content=content,
                    html_content=html_content)
        
        mail.subject = subject
        mail.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=data['is_sandbox_mode']))
        
        if data['type'] == 'SINGLE':
            personalization = Personalization()
            to = To(email=destination['email'], name=destination['name'])

            for key, value in destination.get('dynamic_data', {}).items():
                personalization.add_substitution(Substitution('{{%s}}' % (key), value))

            personalization.add_to(to)
            personalization.ccs = [Email(email=recipient) for recipient in destination['cc'] or []]
            personalization.bccs = [Email(email=recipient) for recipient in destination['bcc'] or []]
            mail.add_personalization(personalization)
        else:
            for destination in data['payload']['destinations']:
                email = destination.get('email')
                personalization = Personalization()
                to_email = To(email=email)

                for key, value in destination.get('dynamic_data', {}).items():
                    personalization.add_substitution(Substitution('{{%s}}' % (key), value))

                personalization.add_to(to_email)
                personalization.ccs = [Email(email=recipient) for recipient in destination['cc'] or []]
                personalization.bccs = [Email(email=recipient) for recipient in destination['bcc'] or []]
                personalization.subject = destination['subject'] if destination['subject'] is not None else subject
                mail.add_personalization(personalization)
            
        self._client.send(mail)


    def register_template(self, name, subject, content, is_html) -> str:
        """
        Create a new template, create a version for the template, then
        activate the already created version.
        """
        # Create a template
        data = {
            'name': name,
            'generation': 'dynamic',
        }
        resp = self._client.client.templates.post(request_body=data)
        assert resp.status_code == 201, (
            'Fail to create a template in SendGrid with status = {}'
            .format(resp.status_code)
        )
        template_id = resp.to_dict['id']
        # Create a new version for the template
        data = {
            'active': 1,
            'name': name,
            'subject': subject,
        }

        if is_html:
            data['html_content'] = content
        else:
            data['plain_content'] = content
        
        resp = self._client.client.templates._(template_id).versions.post(request_body=data)
        assert resp.status_code == 201, (
            'Fail to upload html content for the template with status = {}'
            .format(resp.status_code)
        )
        version_id = resp.to_dict['id']
        
        # Activate the newly created version
        resp = self._client.client.templates._(template_id).versions._(version_id).activate.post()
        assert resp.status_code == 200, (
            'Fail to activate the version with status = {}'
            .format(resp.status_code)
        )
        return template_id

    def update_template(self, template_id, name, subject, content, is_html) -> str:
        pass

    @property
    def provider_name(self):
        return 'SENDGRID'


class AmazonEmailProviderService(IEmailProviderService):
    def __init__(self):
        pass

    def send_with_template_id(self, data) -> dict:
        """
        """
        return {'status_code': 200}

    def send_with_template(self, data):
        """
        """
        return {'status_code': 200}

    @property
    def provider_name(self):
        return 'AMAZON'
    
    def register_template(self, name, subject, content, is_html) -> str:
        return None
    
    def update_template(self, template_id, name, subject, content, is_html) -> str:
        pass


email_service: IEmailProviderService = SendgridEmailProviderService(credentials=settings.SENDGRID_API_KEY)