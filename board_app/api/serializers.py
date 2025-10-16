import random
from rest_framework import serializers
from board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()

    random_number = serializers.SerializerMethodField()
    class Meta:
        model = Board
        # all other fields of the model without the owner included
        # fields = ['id', 'title', 'owner_id' ...] 

    def get_owner_id(self, obj: Board):
        return obj.owner.id
    
    def get_random_number(self, obj: Board):
        return random.randint(obj.id, obj.user.id)
    

# class ReviewerSerialzer(serializers.ModelSerializer):
#     class Meta:
#         model: User
#         fields = ['id', 'fullname', 'email']


# class AssigneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model: User
#         fields = ['id', 'fullname', 'email']
    

# class TaskAssingenToMeSerializer(serializers.ModelSerializer):
#     reviewer = ReviewerSerialzer(many=False, read_only=True)
#     assignee = AssigneSerializer(many=False, read_only=True)
#     class Meta:
#         model: Task
#         field: '__all__'