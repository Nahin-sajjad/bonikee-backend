import socket

from django.utils import timezone

from apps.users.models import UserLogInfo


class UserLogInfoView:
    """
    Utility class for logging user login and logout information.

    This class provides methods for logging user login and logout times
    along with device information.

    Methods:
    - __init__: Initialize the UserLogInfoView with a user instance.
    - device_info: Get device information from the request.
    - login_time: Log user login time with device information.
    - logout_time: Log user logout time.
    """

    def __init__(self, user) -> None:
        """
        Initialize the UserLogInfoView with a user instance.

        Parameters:
        - user: The user for whom the login and logout times are logged.
        """
        self.queryset = UserLogInfo
        self.user = user

    def device_info(self, request):
        """
        Get device information from the request.

        Parameters:
        - request: HTTP request object containing user agent information.

        Returns:
        - dict: Device information dictionary.
        """
        device_info = {
            "client_ip": request.META.get("REMOTE_ADDR"),
            "public_ip_address": socket.gethostbyname("api.ipify.org"),
            "is_mobile": request.user_agent.is_mobile,
            "is_tablet": request.user_agent.is_tablet,
            "is_touch_capable": request.user_agent.is_touch_capable,
            "is_pc": request.user_agent.is_pc,
            "is_bot": request.user_agent.is_bot,
            "browser": request.user_agent.browser,
            "browser_family": request.user_agent.browser.family,
            "browser_version": request.user_agent.browser.version,
            "browser_version_string": request.user_agent.browser.version_string,
            "os": request.user_agent.os,
            "os_family": request.user_agent.os.family,
            "os_version": request.user_agent.os.version,
            "os_version_string": request.user_agent.os.version_string,
            "device": request.user_agent.device,
            "device_family": request.user_agent.device.family,
        }
        return device_info

    def login_time(self, request):
        """
        Log user login time with device information.

        Parameters:
        - request: HTTP request object.

        Returns:
        - None
        """
        device_info = self.device_info(request)
        self.queryset.objects.create(user=self.user, device_info=device_info)

    def logout_time(self):
        """
        Log user logout time.

        Parameters:
        - None

        Returns:
        - None
        """
        user_log_info = self.queryset.objects.filter(user_id=self.user.id).last()
        user_log_info.logout_time = timezone.now()
        user_log_info.save()
