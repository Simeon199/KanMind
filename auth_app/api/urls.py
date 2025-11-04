from django.urls import path
from .views import RegistrationView, CustomLoginView

# urlpatterns array old

# urlpatterns = [
#     path('registration/', RegistrationView.as_view(), name='registration'),
#     path('login/', CustomLoginView.as_view(), name='login')
# ]

# urlpatterns array new

urlpatterns = [
    path('api/registration/', RegistrationView.as_view(), name='registration'),
    path('api/login/', CustomLoginView.as_view(), name='loign')
]