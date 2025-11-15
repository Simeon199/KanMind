"""
URL patterns for the tasks_app API.
This module defines the endpoints for task management, including listing, creating,
updating, and deleting tasks, as well as managing task comments and filtering
tasks by assignment or review status.
"""

from django.urls import path
from .views import TasksAssignedOrReviewedView, TaskListCreateView, TaskRetrieveUpdateDestroyView, TaskCommentListView, TaskCommentRetrieveDestroyView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='tasks'), # List all tasks or create a new task
    path('<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='tasks'), # Retrieve, update, or delete a specific task by ID
    path('<int:pk>/comments/', TaskCommentListView.as_view(), name='tasks'), # List comments for a specific task or add a new comment
    path('<int:task_id>/comments/<int:pk>/', TaskCommentRetrieveDestroyView.as_view(), name='task-comment-detail'), # Retrieve or delete a specific comment on a task
    path('assigned-to-me/', TasksAssignedOrReviewedView.as_view(), name='tasks-assigned'), # List tasks assigned to the current user
    path('reviewing/', TasksAssignedOrReviewedView().as_view(), name='tasks-reviewing') # List tasks the current user is reviewing
]