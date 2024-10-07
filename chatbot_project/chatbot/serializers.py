from rest_framework import serializers
from .models import ActionType, Category, FAQ, Conversation, Message

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class ActionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionType
        fields = ['id', 'name']

class FAQSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    action_type = ActionTypeSerializer(read_only=True)
    action_type_id = serializers.PrimaryKeyRelatedField(queryset=ActionType.objects.all(), source='action_type', write_only=True, allow_null=True)

    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'category_id', 'language', 'action_type', 'action_type_id', 'action_data']

    def validate_answer(self, value):
        try:
            import json
            json.loads(value)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Answer must be a valid JSON string")
        return value

    def validate_action_data(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("action_data must be a dictionary")
        return value

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = '__all__'