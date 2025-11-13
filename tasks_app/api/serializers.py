from rest_framework import serializers
from tasks_app.models import Task, TaskCommentsModel
from django.contrib.auth.models import User

class UserShortSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskSerializer(serializers.ModelSerializer):
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
        """Return the number of comments related to the task."""
        return obj.comments.count()

    def to_representation(self, instance):
        """Customize the serialized output by removing write-only fields."""
        data = super().to_representation(instance)
        for field in ['assignee_id', 'reviewer_id']:
            data.pop(field, None)
        return data

    def validate(self, data):
        """Validate that the assignee and reviewer are members of the board."""
        board = self._get_board(data)
        self._validate_user_membership(data.get('assignee'), board, "Assignee")
        self._validate_user_membership(data.get('reviewer'), board, "Reviewer")
        self._prevent_board_change(data)
        return data
    
    def _get_board(self, data):
        """Retrieve the board from the data or the instance"""
        return data.get('board') or getattr(self.instance, 'board', None)
    
    def _validate_user_membership(self, user, board, role):
        """Ensure the user (assignee/reviewer) is a member of the board."""
        if user and user not in board.members.all():
            raise serializers.ValidationError(f"{role} must be a member of the board.")
        
    def _prevent_board_change(self, data):
        """Prevent changing the board of an existing task."""
        if self.instance and 'board' in data and data['board'] != self.instance.board:
            raise serializers.ValidationError("Changing the board of a task is not allowed")
    
class TaskCommentsSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskCommentsModel
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username