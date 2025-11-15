from tasks_app.models import Task, TaskCommentsModel
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCommentAuthor, IsMemberOfBoard, IsAuthenticatedAndRelatedToTask, IsAuthenticatedAndAssignee, IsAuthenticatedAndReviewer
from .serializers import TaskSerializer, TaskCommentsSerializer
from django.db import models

import logging

logger = logging.getLogger(__name__)

class TasksAssignedOrReviewedView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated] # Ehemals IsMemberOfBoard

    def get_queryset(self):
        user = self.request.user
        if 'assigned-to-me' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user),  # Ensure user is member or owner
                assignee=user,
            ).distinct()
        elif 'reviewing' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user),
                reviewer=user,
            ).distinct()
        else:
            return Task.objects.none()  # Fallback, shouldn't happen
        
    # Optional: If allowing creation, adjust perform_create to set assignee/reviewer based on endpoint
    def perform_create(self, serializer):
        if 'assigned-to-me' in self.request.path:
            serializer.save(assignee=self.request.user)
        elif 'reviewing' in self.request.path:
            serializer.save(reviewer=self.request.user)
        else:
            serializer.save()
       
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
class TaskCommentListView(generics.ListCreateAPIView):
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        return TaskCommentsModel.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('pk')
        serializer.save(
            author=self.request.user,
            task=Task.objects.get(pk=task_id)
        )

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
class TaskCommentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = TaskCommentsModel.objects.all()
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    
    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('pk')
        return TaskCommentsModel.objects.filter(
            task_id=task_id,
            pk=comment_id
        )