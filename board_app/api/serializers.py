import random
from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        class Meta:
            model = Board
            fields = ['title', 'members']

# class BoardSerializer(serializers.ModelSerializer):
#     members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
#     owner_id = serializers.IntegerField(source='owner_id', read_only=True)
#     member_count = serializers.SerializerMethodField(read_only=True)
#     ticket_count = serializers.IntegerField(read_only=True)
#     tasks_to_do_count = serializers.IntegerField(read_only=True)
#     tasks_high_prio_count = serializers.IntegerField(read_only=True)
#     id = serializers.IntegerField(read_only=True)
    
#     class Meta:
#         model = Board
#         fields = [
#             'id', 'title', 'members', 'member_count', 'ticket_count',
#             'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
#         ]

#     def get_member_count(self, obj):
#         return obj.members.count()
    
#     def create(self, validated_data):
#         members = validated_data.pop('members', [])
#         owner = self.context['request'].user
#         board = Board.objects.create(
#             owner=owner,
#             title=validated_data.get('title'),
#             ticket_count=validated_data.get('ticket_count', 0),
#             tasks_to_do_count=validated_data.get('tasks_to_do_count', 0),
#             tasks_high_prio_count=validated_data.get('tasks_high_prio_count', 0)
#         )
#         board.members.set(members)
#         board.member_count = board.members_count()
#         board.save()
#         return board