from rest_framework_simplejwt.tokens import RefreshToken


class Tokens:
    def get_tokens_for_user(self, user):
        """
        Generate access and refresh tokens for the authenticated user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def set_cookie(self, response, key, cookie_settings, token, token_lifetime):
        """
        Set the cookie in the response with appropriate settings.
        """
        response.set_cookie(
            key=key,
            value=token,
            expires=token_lifetime,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )
