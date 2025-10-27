from tasks_app.models import Task
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskSerializer

class TasksAssignedView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

# New lines of code

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Show tasks where user is a board member or assignee/reviewer
        return Task.objects.filter(board__members=user).distinct()
    
    def perform_create(self, serializer):
        serializer.save() # validation already enforces members

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # ensure user can access this object
        user = self.request.user
        return Task.objects.filter(board__members=user)