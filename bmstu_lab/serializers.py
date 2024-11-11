from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Instruction, Tool, ToolInstruction


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = [
            'id', 'title', 'description', 'description_detail',
            'status', 'image_url'
        ]
        read_only_fields = ['id']


class InstructionSerializer(serializers.ModelSerializer):
    moderator = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), allow_null=True
    )
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), allow_null=True
    )
    tools = serializers.SerializerMethodField()

    def get_tools(self, instruction):
        tool_instructions = ToolInstruction.objects.filter(
            instruction=instruction)
        tools = [tool_instruction.tool for tool_instruction in tool_instructions]
        serializer = ToolSerializer(tools, many=True)
        return serializer.data

    class Meta:
        model = Instruction
        fields = [
            'id', 'status', 'creation_time', 'submit_date', 'complete_date',
            'moderator', 'user', 'intent', 'tools'
        ]
        read_only_fields = ['id', 'creation_time']


class ToolInstructionSerializer(serializers.ModelSerializer):
    tool = serializers.SlugRelatedField(
        slug_field='title', queryset=Tool.objects.all(), allow_null=True
    )
    instruction = serializers.PrimaryKeyRelatedField(
        queryset=Instruction.objects.all(), allow_null=True
    )

    class Meta:
        model = ToolInstruction
        fields = [
            'id', 'tool', 'instruction', 'tool_parameter'
        ]
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name',
                  'last_name', 'email', 'date_joined')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password',
                  'first_name', 'last_name', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
