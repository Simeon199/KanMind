from django.urls import path
from .views import TasksAssignedOrReviewedView, TaskListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task'),
    path('assigned-to-me/', TasksAssignedOrReviewedView.as_view(), name='tasks'),
    path('reviewing/', TasksAssignedOrReviewedView().as_view(), name='tasks')
]