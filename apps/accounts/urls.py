from django.urls import path
from .views import PermissionView, GroupView, GroupDetailView

urlpatterns = [
    path("permission/", PermissionView.as_view()),
    path("group/", GroupView.as_view()),
    path("group/<int:pk>/", GroupDetailView.as_view()),
]
