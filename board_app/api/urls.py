from django.urls import path
from .views import BoardView, BoardRetrieveUpdateDestroyView

urlpatterns = [
    path('', BoardView.as_view(), name='boards'),
    path('<int:pk>/', BoardRetrieveUpdateDestroyView.as_view(), name='board-detail')
]