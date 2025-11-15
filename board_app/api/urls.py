"""
URL patterns for the board_app API.
This module defines the endpoints for board-related operations,
including listing, creating, updating, and deleting boards,
as well as checking user emails.
"""

from django.urls import path
from .views import BoardView, BoardRetrieveUpdateDestroyView, EmailCheckView

urlpatterns = [
    path('boards/', BoardView.as_view(), name='boards'), # List all boards for the user or create a new board
    path('boards/<int:pk>/', BoardRetrieveUpdateDestroyView.as_view(), name='board-detail'), # Retrieve, update, or delete a specific board by ID
    path('email-check/', EmailCheckView.as_view(), name='email-check') # Check if a user exists by email address
]