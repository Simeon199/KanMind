from tasks_app.models import Task, TaskCommentsModel
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCommentAuthor
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
class TaskCommentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = TaskCommentsModel.objects.all()
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        # task_id = self.kwargs.get('task_id')
        task_id = self.kwargs.get('pk')
        comment_id = self.kwargs.get('comment_id')
        return TaskCommentsModel.objects.filter(
            task_id=task_id,
            pk=comment_id
        )