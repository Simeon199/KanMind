from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        owner_id = serializers.SerializerMethodField()
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        member_count = serializers.SerializerMethodField()
        # ticket_count = serializers.SerializerMethodField()
        # tasks_to_do_count = serializers.SerializerMethodField()
        # tasks_high_prio_count = serializers.SerializerMethodField()
        # ticket_count = serializers.IntegerField(read_only=True)
        # tasks_to_do_count = serializers.IntegerField(read_only=True)
        # tasks_high_prio_count = serializers.IntegerField(read_only=True)
        id=serializers.IntegerField(read_only=True)

        class Meta:
            model = Board
            fields = [
                  'id', 'title', 'members', 'member_count', 'owner_id'
            ]

        def get_owner_id(self, obj: Board):
              return obj.owner.id
        
        def get_member_count(self, obj: Board):
              if not obj.members.exists():
                    return 0
              return obj.members.count()
        
      #   def get_ticket_count(self, obj:Board):
      #         if not obj.ticket_count:
      #               return 0
      #         return obj.ticket_count
        
      #   def get_tasks_to_do_count(self, obj:Board):
      #         if not obj.tasks_to_do_count:
      #               return 0
      #         return obj.tasks_to_do_count
        
      #   def get_tasks_high_prio_count(self, obj:Board):
      #         if not obj.tasks_high_prio_count:
      #               return 0
      #         return obj.tasks_high_prio_count
        
      #   def create(self, validated_data):
      #         members = validated_data.pop('members', [])
      #         board = Board.objects.create(**validated_data)
      #         board.members.set(members)
      #         return board