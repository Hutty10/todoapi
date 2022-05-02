from ast import Expression
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, force_bytes, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from .serializers import RegisterSerializer, LoginSerializer, RequestPasswordResetEmailSerializer, SetNewPasswordSerializer
from .models import User

# Create your views here.


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
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relative_link = reverse('account:password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
            absurl = f'http://{current_site+relative_link}'

            email_subject = 'Reset your password'
            email_body = f'Hi  please click on the link below to reset your password \n{absurl}'
            
            user.send_email(email_subject, email_body)
        return Response({'success': 'we have sent a link to reset your password'}, status=status.HTTP_200_OK)


class PassowrdTokenCheckView(generics.GenericAPIView):

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid anymore please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message': 'credential valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid anymore please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)