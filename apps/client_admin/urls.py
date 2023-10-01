from django.urls import path
from apps.client_admin.views.preference import PreferenceView, PreferenceDetailView

urlpatterns = [
    path("preference/", PreferenceView.as_view(), name="preference"),
    path(
        "preference/<int:pk>/", PreferenceDetailView.as_view(), name="preference-detail"
    ),
]
