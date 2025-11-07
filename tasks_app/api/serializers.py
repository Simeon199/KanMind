from rest_framework import serializers
from tasks_app.models import Task, TaskCommentsModel
from django.contrib.auth.models import User

class UserShortSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 
            'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 
            'due_date', 'comments_count'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('assignee_id', None)
        data.pop('reviewer_id', None)
        return data
    
    def validate(self, data):
        board = data.get('board') or getattr(self.instance, 'board', None)
        assignee = data.get('assignee', getattr(self.instance, 'assignee', None))
        reviewer = data.get('reviewer', getattr(self.instance, 'reviewer', None))

        # Check assignee and reviewer are board members (if provided)
        if assignee and assignee not in board.members.all():
            raise serializers.ValidationError("Assignee must be a member of the board.")
        if reviewer and reviewer not in board.members.all():
            raise serializers.ValidationError("Reviewer must be a member of the board.")
        
        # Prevent changing the board on update
        if self.instance and 'board' in data and data['board'] != self.instance.board:
            raise serializers.ValidationError("Changing the board of a task is not allowed.")
        
        return data
    
class TaskCommentsSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskCommentsModel
        fields = ['id', 'task', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username