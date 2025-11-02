from rest_framework import serializers
from board_app.models import Board, SingleBoard
from django.contrib.auth.models import User

# Fehler im Preview: Board object has no attribute owner

class BoardSerializer(serializers.ModelSerializer):
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
        member_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            # exclude = '[owner]'
            fields = '__all__'

        def get_member_count(self, obj):
            return len(obj.members.all())
        
# Im SingleBoardSerializer könnte es Sinn machen, zu definieren, dass das board_id-Feld sichbar ist. 
# Anschließend kann die SingleBoardView von dem SingleBoardSerializer erben, um sicherzustellen, dass die 
# board_id angezeigt wird.

class SingleBoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
         model = SingleBoard
         fields = '__all__'