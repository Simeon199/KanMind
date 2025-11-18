from rest_framework import serializers
from board_app.models import Board
from tasks_app.api.serializers import TaskSerializerWithoutBoard, UserShortSerializer
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
        """
        Serializer for the Board model.
        Handles serialization and deserialization of board data, including members,
        owner information, computed fields for task counts and member count. Supports creating and updating boards
        with proper ownership and membership management.
        """
        members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False, write_only=True)
        owner_id = serializers.IntegerField(source='owner.id', read_only=True)
        member_count = serializers.SerializerMethodField()
        ticket_count = serializers.SerializerMethodField() 
        tasks_to_do_count = serializers.SerializerMethodField()
        tasks_high_prio_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            fields = ['id', 'title', 'members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
            read_only_fields = ['owner_id', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

        def get_member_count(self, obj):
            """
            Return the number of members in the board.

            Args:
               obj: The board instance.
            Returns:
               int: The count of members.
            """
            return len(obj.members.all())
        
        def get_ticket_count(self, obj):
             """
             Return the total number of tasks associated with the board.

             Args: 
                obj: The Board instance.

             Returns:
                int: The total count of tasks.
             """
             return obj.tasks.count()
        
        def get_tasks_to_do_count(self, obj):
             """
             Return the number of tasks with status "to-do".
             
             Args:
               obj: The Board instance.

             Returns:
               int: The count of "to-do" tasks.
             """
             return obj.tasks.filter(status='to-do').count()
        
        def get_tasks_high_prio_count(self, obj):
             """
             Return the number of tasks with priority "high".

             Args:
                obj: The Board instance.

             Returns:
                int: The count of high-priority tasks.
             """
             return obj.tasks.filter(priority='high').count()
        
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
    Handles detailed serialization for retrieving a single board, including full member and task details.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserShortSerializer(many=True, read_only=True)
    tasks = TaskSerializerWithoutBoard(many=True, read_only=True) 
    
    class Meta:
         model = Board
         fields = ['id', 'title', 'owner_id', 'members', 'tasks']

class BoardUpdateSerializer(serializers.ModelSerializer):
     """
     Serializer for updating a board (PATCH).
     Excludes tasks and includes owner_data and members_data with full user details.
     """
     owner_data = UserShortSerializer(source='owner', read_only=True) 
     members_data = UserShortSerializer(source='members', many=True, read_only=True) 

     class Meta:
          model = Board
          fields = ['id', 'title', 'owner_data', 'members_data'] 