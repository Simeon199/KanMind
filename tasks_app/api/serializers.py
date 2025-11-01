from rest_framework import serializers
from tasks_app.models import Task, TaskCommentsModel, Board
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
    
class TaskCommentsSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskCommentsModel
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username