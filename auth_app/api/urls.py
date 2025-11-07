from django.urls import path
from .views import RegistrationView, CustomLoginView

urlpatterns = [
    path('api/registration/', RegistrationView.as_view(), name='registration'),
    path('api/login/', CustomLoginView.as_view(), name='loign')
]