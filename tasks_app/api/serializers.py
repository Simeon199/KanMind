from rest_framework import serializers
from tasks_app.models import Task, TaskCommentsModel
from django.contrib.auth.models import User

class UserShortSerializer(serializers.ModelSerializer):
    """
    Serializer for a shortened User model representation.
    Provides basic user information including a fullname field derived from username.
    """
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    Handles serialization and deserialization of task data, including assignee, reviewer, 
    board members, and validation to ensure assignments are valid.
    """
    # Output 
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)

    # Accept IDs (preferred keys)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)
    
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 
            'assignee', 'assignee_id', 'reviewer', 'reviewer_id',
            'due_date', 'comments_count'
        ]
    
    def get_comments_count(self, obj):
        """
        Return the number of comments related to the task.
        
        Args:
           obj: The task instance.

        Returns:
           int: The count of comments.
        """
        return obj.comments.count()

    def to_representation(self, instance):
        """
        Customize the serialized output by removing write-only fields.
        
        Args: 
           instance: The Task instance being serialized.

        Returns:
           dict: The customized serialized data.
        """
        data = super().to_representation(instance)
        for field in ['assignee_id', 'reviewer_id']:
            data.pop(field, None)
        return data

    def validate(self, data):
        """
        Validate that the assignee and reviewer are members of the board.

        Args:
           data: The input data to validate.

        Returns:
           dict: The validated data.

        Raises:
           serializers.ValidationError: If validation fails.
        """
        board = self._get_board(data)
        self._validate_user_membership(data.get('assignee'), board, "Assignee")
        self._validate_user_membership(data.get('reviewer'), board, "Reviewer")
        self._prevent_board_change(data)
        return data
    
    def _get_board(self, data):
        """
        Retrieve the board from the data or the instance.

        Args:
           data: The input data.

        Returns:
           Board or None: The board instance if found.
        """
        return data.get('board') or getattr(self.instance, 'board', None)
    
    def _validate_user_membership(self, user, board, role):
        """
        Ensure the user (assignee/reviewer) is a member of the board.

        Args:
           user: The user to validate.
           board: The board to check agains.
           role: The role being assigned (e.g., 'Assignee')

        Raises:
           serializers.ValidationError: If the user is not a member.
        """
        if user and user not in board.members.all():
            raise serializers.ValidationError(f"{role} must be a member of the board.")
        
    def _prevent_board_change(self, data):
        """
        Prevent changing the board of an existing task.

        Args:
           data: The input data.

        Raises:
           serializers.ValidationError: If board change is attempted.
        """
        if self.instance and 'board' in data and data['board'] != self.instance.board:
            raise serializers.ValidationError("Changing the board of a task is not allowed")
        
class TaskSerializerWithoutBoard(TaskSerializer):
    """
    Serializer for Task model without the 'board' field.
    Used in contexts where the board is implied (e.g., nested in board details.)
    """
    class Meta(TaskSerializer.Meta):
        fields = [field for field in TaskSerializer.Meta.fields if field != 'board']
    
class TaskCommentsSerializer(serializers.ModelSerializer):
    """
    Serializer for the TaskCommentsModel.
    Handles serialization of task comments, including author information.
    """
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskCommentsModel
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """
        Return the author's full name or username.

        Args:
           obj: The TaskCommentsModel instance.

        Returns:
           str: The author's name.
        """
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username