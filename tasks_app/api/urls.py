from django.urls import path
from .views import TasksAssignedOrReviewedView, TaskListCreateView, TaskRetrieveUpdateDestroyView, TaskCommentListView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='tasks'),
    path('<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='tasks'),
    path('<int:pk>/comments/', TaskCommentListView.as_view(), name='tasks'),
    path('assigned-to-me/', TasksAssignedOrReviewedView.as_view(), name='tasks'),
    path('reviewing/', TasksAssignedOrReviewedView().as_view(), name='tasks')
]