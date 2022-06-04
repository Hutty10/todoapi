import os
import jwt
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, force_bytes, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegisterSerializer, LoginSerializer, RequestPasswordResetEmailSerializer, SetNewPasswordSerializer
from .models import User
from .permissions import IsOwnerOnly

# Create your views here.

class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = RegisterSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        access_token = user.tokens()['access']
        current_site = get_current_site(request).domain
        relative_link = reverse('auth:verify_email')
        absurl = f'http://{current_site+relative_link}?token={access_token}'
        
        email_subject = 'Activate your account'
        email_body = f'Hi {user.username} please click on the link below to activate your account \n{absurl}\nthis link will expire in 30 minutes'
        
        user.send_email(email_subject, email_body)
            
        

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        


class VerifyEmail(generics.GenericAPIView):
    
    def get(self, request):
        token = request.GET.get('token')
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            login(request, user)
            return Response({'success': 'Email successfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relative_link = reverse('account:password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
            redirect_url = request.data.get('redirect_url','')
            absurl = f'http://{current_site+relative_link}'

            email_subject = 'Reset your password'
            email_body = f'Hi  please click on the link below to reset your password \n{absurl}?redirect_url={redirect_url}'
            
            user.send_email(email_subject, email_body)
        return Response({'success': 'we have sent a link to reset your password'}, status=status.HTTP_200_OK)


class PassowrdTokenCheckView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url)>3:
                return CustomRedirect(f'{redirect_url}?token_valid=True&message=Credentials-valid&uidb64={uidb64}&token={token}')
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return CustomRedirect(redirect_url+'?token_valid=False')
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, Please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)


class AuthUser(generics.GenericAPIView):
    # import pdb;pdb.set_trace()

    serializer_class = RegisterSerializer
    permission_classes = [IsOwnerOnly]
    
    def get(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)