from rest_framework import serializers
from board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
        owner_id = serializers.SerializerMethodField()
        class Meta:
            model = Board
            # fields = ['title', 'members']

        def get_owner_id(self, obj: Board):
              return obj.owner.id