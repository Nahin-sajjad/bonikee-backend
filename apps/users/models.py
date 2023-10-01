from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# Custom user manager for the User model
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


# Custom User model
class User(AbstractUser):
    # Remove the 'username' field and use 'email' as the unique identifier
    username = None
    email = models.EmailField(
        blank=False,
        max_length=254,
        unique=True,
        db_index=True,
        verbose_name="email address",
    )
    user_type = models.CharField(max_length=250, blank=True, null=True)
    USERNAME_FIELD = "email"  # Use 'email' as the login identifier
    REQUIRED_FIELDS = []  # No additional required fields

    # Define custom fields and attributes here if needed

    objects = UserManager()  # Use the custom UserManager

    def __str__(self):
        return self.email


# Model for logging user login and logout information
class UserLogInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_log")
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    device_info = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.user.email
