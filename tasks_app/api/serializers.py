from rest_framework import serializers
from tasks_app.models import Task
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    # assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    # reviewer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Task
        fields = '__all__'

    # New lines of code

    def validate(self, attrs):
        board = attrs.get('board')
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if board is None:
            raise serializers.ValidationError({"board": "Board is required."})
        
        members = board.members.all()
        if assignee not in members:
            raise serializers.ValidationError({"assignee": "Assignee must be a member of the board."})
        if reviewer not in members:
            raise serializers.ValidationError({"reviewer must be a member of the board."})
        return attrs