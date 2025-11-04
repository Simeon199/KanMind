from rest_framework import serializers
from board_app.models import Board, SingleBoard
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
        owner_id = serializers.IntegerField(source='owner.id', read_only=True)
        member_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            fields = ['id', 'title', 'members', 'member_count', 'owner_id']
            read_only_fields = ['owner_id']

        def get_member_count(self, obj):
            return len(obj.members.all())
        
        def create(self, validated_data):
             members = validated_data.pop('members', [])
             validated_data.pop('owner', None)
             board = Board.objects.create(owner=self.context['request'].user, **validated_data)
             if members:
                  board.members.set(members)
             return board
        
        def update(self, instance, validated_data):
             members = validated_data.pop('members', None)
             for attr, value in validated_data.items():
                  setattr(instance, attr, value)
             instance.save()
             if members is not None:
                  instance.members.set(members)
             return instance

class SingleBoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
         model = SingleBoard
         fields = '__all__'