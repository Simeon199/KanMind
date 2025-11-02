from django.urls import path
from .views import BoardView, SingleBoardView, BoardRetrieveUpdateDestroyView

urlpatterns = [
    path('', BoardView.as_view(), name='boards'),
    path('<int:pk>/', SingleBoardView.as_view(), name='singleBoardView'),
    path('<int:pk>/', BoardRetrieveUpdateDestroyView.as_view(), name='singleBoardViewUpdated')
]