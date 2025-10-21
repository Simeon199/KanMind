from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        owner_id = serializers.SerializerMethodField()

        #new lines
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        member_count = serializers.SerializerMethodField()
        ticket_count = serializers.IntegerField(read_only=True)
        tasks_to_do_count = serializers.IntegerField(read_only=True)
        tasks_high_prio_count = serializers.IntegerField(read_only=True)
        id=serializers.IntegerField(read_only=True)

        class Meta:
            model = Board
            fields = [ # 'id'
                  'id', 'title', 'members', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
            ]

        def get_owner_id(self, obj: Board):
              return obj.owner.id
        
        def get_member_count(self, obj):
              return obj.members.count()
        
        def create(self, validated_data):
              members = validated_data.pop('members', [])
              board = Board.objects.create(**validated_data)
              board.members.set(members)
              board.member_count = board.members.count()
              board.save()
              return board