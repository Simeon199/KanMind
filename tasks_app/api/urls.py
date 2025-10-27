from django.urls import path
from .views import TasksAssignedView, TaskListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task'),
    path('assigned-to-me/', TasksAssignedView.as_view(), name='tasks'),
]