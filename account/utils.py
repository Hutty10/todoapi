# from django.core.mail import EmailMessage

# class Utils:

#     @staticmethod
#     def send_email(user_data, absurl):
#         email_subject = 'Verify your email'
#         email_body = f'Hi {user_data["username"]} use the link below to verify your email \n{absurl}'
#         email = EmailMessage(subject=email_subject, body=email_body, to=[user_data["email"]])
#         email.send()