from rest_framework import serializers
from board_app.models import Board, SingleBoard
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        """
        Serializer for the Board model.
        Handles serialization and deserialization of board data, including members,
        owner information, and member count. Supports creating and updating boards
        with proper ownership and membership management.
        """
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
        owner_id = serializers.IntegerField(source='owner.id', read_only=True)
        member_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            fields = ['id', 'title', 'members', 'member_count', 'owner_id']
            read_only_fields = ['owner_id']

        def get_member_count(self, obj):
            """
            Return the number of members in the board.

            Args:
               obj: The board instance.
            Returns:
               int: The count of members.
            """
            return len(obj.members.all())
        
        def create(self, validated_data):
             """
             Create a new board instance with the authenticated user as owner.

             Args:
                validated_data: The validated data from the request.
             Returns:
                Board: The created board instance.
             """
             members = validated_data.pop('members', [])
             validated_data.pop('owner', None)
             board = Board.objects.create(owner=self.context['request'].user, **validated_data)
             if members:
                  board.members.set(members)
             return board
        
        def update(self, instance, validated_data):
             """
             Update an existing board instance.

             Args:
                instance: The existing Board instance to update.
                validated_data: The validated data from the request.

             Returns:
                Board: The updated board instance.
             """
             members = validated_data.pop('members', None)
             for attr, value in validated_data.items():
                  setattr(instance, attr, value)
             instance.save()
             if members is not None:
                  instance.members.set(members)
             return instance

class SingleBoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the SingleBoard model.
    Handles serialization and deserialization of single board data,
    including members as primary key references.
    """
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    
    class Meta:
         model = SingleBoard
         fields = '__all__'