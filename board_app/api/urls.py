from django.urls import path
from .views import BoardView, BoardRetrieveUpdateDestroyView, EmailCheckView

urlpatterns = [
    path('boards/', BoardView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardRetrieveUpdateDestroyView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check')
]