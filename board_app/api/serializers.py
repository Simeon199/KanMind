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