from django.urls import path
from .views import TasksAssignedOrReviewedView, TaskListCreateView, TaskRetrieveUpdateDestroyView, TaskCommentListView, TaskCommentRetrieveDestroyView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='tasks'),
    path('<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='tasks'),
    path('<int:pk>/comments/', TaskCommentListView.as_view(), name='tasks'),
    path('<int:task_id>/comments/<int:pk>/', TaskCommentRetrieveDestroyView.as_view(), name='task-comment-detail'),
    path('assigned-to-me/', TasksAssignedOrReviewedView.as_view(), name='tasks-assigned'),
    path('reviewing/', TasksAssignedOrReviewedView().as_view(), name='tasks-reviewing')
]