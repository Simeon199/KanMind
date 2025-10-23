from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        member_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            fields = '__all__'

        def get_member_count(self, obj):
            return len(obj.members.all())
        
        # def create(self, validated_data):
        #      instance = validated_data.pop('board', None)
        #      if instance is None:
        #           raise serializers.ValidationError("A Board instance must be provided")
        #      instance.ticket_count = 0
        #      instance.tasks_to_do_count = 0
        #      instance.tasks_high_prio_count = 0

        #      return super().create(validated_data)