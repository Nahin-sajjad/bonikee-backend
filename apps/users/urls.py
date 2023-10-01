from django.urls import path

from apps.users.views.auth.custom_refresh_token import CustomTokenRefreshView
from apps.users.views.auth.login import LoginView
from apps.users.views.auth.logout import LogoutView
from apps.users.views.auth.registration import RegistrationView
from apps.users.views.auth.verify_token import VerifyToken
from apps.users.views.userinfo.update_user import UpdateUserInformationView
from apps.users.views.userinfo.userlist import UserListView
from apps.users.views.auth.tenant_user import TenantUserView
from apps.users.views.auth.forgot_password import (
    ForgotPasswordSendResetLinkView,
    ForgotPasswordActivationLinkView,
    PasswordResetView,
)
from apps.users.views.auth.change_password import ChangePasswordView
from apps.users.views.auth.group_info import UserGroupInfoView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("tenant/user/", TenantUserView.as_view(), name="tenant_user"),
    path("login/", LoginView.as_view(), name="login"),
    path("change/password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "forgot/password/",
        ForgotPasswordSendResetLinkView.as_view(),
        name="forgot_password",
    ),
    path(
        "forgot/password/<str:uid>/<str:token>/",
        ForgotPasswordActivationLinkView.as_view(),
        name="password_reset_link",
    ),
    path(
        "reset/password/<str:uid>/<str:token>/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path("token/verify/", VerifyToken.as_view(), name="token_verify"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path(
        "group/info/",
        UserGroupInfoView.as_view(),
        name="user_group_info",
    ),
    path("list/", UserListView.as_view()),
    path("update/<int:pk>/", UpdateUserInformationView.as_view()),
    path("logout/", LogoutView.as_view()),
]
