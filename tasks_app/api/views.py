from tasks_app.models import Task, TaskCommentsModel
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskSerializer, TaskCommentsSerializer

class TasksAssignedOrReviewedView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
class TaskCommentListView(generics.ListCreateAPIView):
    queryset = TaskCommentsModel.objects.all()
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated]

    # New lines of code
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
class TaskCommentRetrieveDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskCommentsModel.objects.all()
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated]