from tasks_app.models import Task, TaskCommentsModel
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCommentAuthor, IsMemberOfBoard, IsAuthenticatedAndAssignee, IsAuthenticatedAndReviewer
from .serializers import TaskSerializer, TaskCommentsSerializer

class TasksAssignedOrReviewedView(generics.ListCreateAPIView): # generics.ListCreateAPIView
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedAndAssignee, IsAuthenticatedAndReviewer]

class TaskListCreateView(generics.ListCreateAPIView): # generics.ListCreateAPIView
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
        task_id = self.kwargs.get('task_id') # pk
        comment_id = self.kwargs.get('pk')
        return TaskCommentsModel.objects.filter(
            task_id=task_id,
            pk=comment_id
        )