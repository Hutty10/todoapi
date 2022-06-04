from django.urls import path
from django.conf.urls import handler404
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, VerifyEmail, LoginView, RequestPasswordResetEmail, PassowrdTokenCheckView, SetNewPasswordView, AuthUser

app_name = 'account'

urlpatterns = [
    # register user
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmail.as_view(), name='verify_email'),
    # login user
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # reset password
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='password_reset_email'),
    path('password-reset/<uidb64>/<token>/', PassowrdTokenCheckView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete', SetNewPasswordView.as_view(), name='password_reset_complete'),
    path('authuser/', AuthUser.as_view(), name='authuser')
]

# handler400 = 'utils.views.error_400'
# handler403 = 'utils.views.error_403'