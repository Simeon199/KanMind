from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        class Meta:
            model = Board
            fields = ['title', 'members']