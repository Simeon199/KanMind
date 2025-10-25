from tasks_app.models import Task
from rest_framework import generics
from .serializers import TaskSerializer

class TaskView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer