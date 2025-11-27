from tasks_app.models import Task, TaskCommentsModel
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCommentAuthor, IsMemberOfBoard, IsTaskCreator, IsTaskCreatorOrBoardOwner
from .serializers import TaskSerializer, TaskCommentsSerializer
from django.db import models
from rest_framework.exceptions import NotFound

class TasksAssignedOrReviewedView(generics.ListCreateAPIView):
    """
    API view for listing and creating tasks assigned to or reviewed by the authenticated user.
    Handles endpoints for tasks assigned to the user or tasks they are reviewing.
    Requires the user to be authenticated.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        """
        Return a queryset of tasks based on the endpoint path.
        For 'assigned-to-me', returns tasks where the user is the assignee.
        For 'reviewing', returns tasks where the user is the reviewer.
        Filters to include only tasks from boards where the user is a member or owner.

        Returns:
            Queryset: Filtered tasks for the authenticated user.
        """
        user = self.request.user
        if 'assigned-to-me' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user), 
                assignee=user,
            ).distinct()
        elif 'reviewing' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user),
                reviewer=user,
            ).distinct()
        else:
            return Task.objects.none()
        
    def perform_create(self, serializer):
        """
        Save the serializer with the appropriate user assigned based on the endpoint.
        For 'assigned-to-me', sets the assignee to the current user.
        For 'reviewing', sets the reviewer to the current user.

        Args:
           serializer: The TaskSerializer instance.
        """
        if 'assigned-to-me' in self.request.path:
            serializer.save(assignee=self.request.user)
        elif 'reviewing' in self.request.path:
            serializer.save(reviewer=self.request.user)
        else:
            serializer.save()
       
class TaskListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating tasks.
    Lists tasks from boards where the user is a member.
    Creates new tasks with proper permissions.
    Requires the user to be authenticated and member of the board.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        """
        Return a queryset of tasks from boards where the user is a member or owner.

        Returns:
            Queryset: Filtered tasks for the authenticated user.
        """
        user = self.request.user
        return Task.objects.filter(
            models.Q(board__members=user) | models.Q(board__owner=user)
        ).distinct()
    
class TaskCommentListView(generics.ListCreateAPIView):
    """
    API view for listing and creating comments on a specific task.
    Lists comments for the given task.
    Creates new comments with the authenticated user as author.
    Requires the user to be authenticated and a member of the board.
    """
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        """
        Return a queryset of comments for the specified task.

        Returns: 
            Queryset: Comments for the task identified by pk in the URL.
        """
        task_id = self.kwargs.get('pk')
        return TaskCommentsModel.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """
        Save the serializer with the authenticated user as the author and the specified task.

        Args:
           serializer: The TaskCommentsSerializer instance.
        """
        task_id = self.kwargs.get('pk')
        serializer.save(
            author=self.request.user,
            task=Task.objects.get(pk=task_id)
        )

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual tasks.
    Filters tasks to those from boards where the user is a member.
    Requires the user to be authenticated and a member of the board for GET/PATCH.
    For DELETE, requires the user to be the task creator or the board owner.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Return permissions based on the HTTP method:
        - For DELETE: Only the task creator or board owner can delete.
        - For GET/PATCH: User must be a board member or owner.
        
        Returns:
           list: List of permission instances.
        """
        if self.request.method == 'DELETE':
            return [IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsMemberOfBoard()]

    def get_queryset(self):
        """
        Return a queryset of tasks from boards where the user is a member or owner.

        Returns:
            Queryset: Filtered tasks for the authenticated user.
        """
        user = self.request.user
        q_object = models.Q(board__members=user) | models.Q(board__owner=user)
        queryset = Task.objects.filter(q_object).distinct()
        return queryset
    
    def get_object(self):
        """
        Retrieve the tasks object, raising NotFound if the task does not exist.

        Returns:
           Task: The task instance.

        Raises:
            NotFound: If the task with the given ID does not exist
        """
        try:
            return super().get_object()
        except Exception:
            raise NotFound("Task not found.")
    
class TaskCommentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    API view for retrieving and deleting individual comments on a task.
    Filters comments to those on the specified task.
    Requires the user to be authenticated and the author of the comment.
    """
    queryset = TaskCommentsModel.objects.all()
    serializer_class = TaskCommentsSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    
    def get_queryset(self):
        """
        Return a queryset of the specific comment for the given task and comment IDs.

        Returns:
            Queryset: The comment matching the task_id and pk.
        """
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('pk')
        return TaskCommentsModel.objects.filter(
            task_id=task_id,
            pk=comment_id
        )