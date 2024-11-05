from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.db import connection
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.db.models import Max
from .minio import *
from django.contrib.auth import authenticate


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(['GET'])
def get_tools_list(request):
    tool_title = request.GET.get('tool_title', '')

    tools = Tool.objects.filter(status='active').filter(
        title__istartswith=tool_title)

    serializer = ToolSerializer(tools, many=True)

    draft_instruction = Instruction.objects.filter(status='draft').first()

    response = {
        'tools': serializer.data,
        'draft_instruction': draft_instruction.id if draft_instruction else None,
        'tools_to_instruction': len(draft_instruction.toolinstruction_set.all()) if draft_instruction else None,
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_tool_by_id(request, tool_id):
    try:
        tool = Tool.objects.get(pk=tool_id)
    except Tool.DoesNotExist:
        return Response({'error': 'Инструмент не найден!'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ToolSerializer(tool, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def create_tool(request):
    tools_data = request.data.copy()
    tools_data.pop('image_url', None)
    serializer = ToolSerializer(data=tools_data)
    serializer.is_valid(raise_exception=True)

    new_tool = serializer.save()
    return Response(ToolSerializer(new_tool).data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_tool(request, tool_id):
    try:
        tool = Tool.objects.get(pk=tool_id)
    except Tool.DoesNotExist:
        return Response({'error': 'Инструмент не найден'}, status=status.HTTP_404_NOT_FOUND)

    tool_data = request.data.copy()
    tool_data.pop('image_url', None)

    serializer = ToolSerializer(tool, data=tool_data, partial=True)
    serializer.is_valid(raise_exception=True)
    updated_tool = serializer.save()

    image_url = request.data.get('image_url')
    if image_url:
        updated_tool.image_url = image_url
        updated_tool.save()

    return Response(ToolSerializer(updated_tool).data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_tool(request, tool_id):
    try:
        tool = Tool.objects.get(pk=tool_id)
    except Tool.DoesNotExist:
        return Response({'error': 'Инструмент не найден'}, status=status.HTTP_404_NOT_FOUND)

    tool.status = 'deleted'
    tool.save()

    tools = Tool.objects.filter(status='active')
    serializer = ToolSerializer(tools, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def update_tool_image(request, tool_id):
    try:
        tool = Tool.objects.get(pk=tool_id)
    except Tool.DoesNotExist:
        return Response({"Ошибка": "Инструмент не найден"}, status=status.HTTP_404_NOT_FOUND)

    if 'image' not in request.FILES:
        return Response({"error": "Изображение не предоставлено"}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']

    # Use the add_pic function to upload the image to Minio
    result = add_pic(tool, image_file)

    if isinstance(result, Response) and 'error' in result.data:
        return result

    serializer = ToolSerializer(tool)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_tool_to_instruction(request, tool_id):
    try:
        tool = Tool.objects.get(pk=tool_id)
    except Tool.DoesNotExist:
        return Response({'error': 'Инструмент не найден'}, status=status.HTTP_404_NOT_FOUND)

    draft_instruction = Instruction.objects.filter(status='draft').first()

    if draft_instruction is None:
        draft_instruction = Instruction.objects.create(
            creation_time=timezone.now(),
            user=User.objects.filter(is_superuser=False).first()
        )
        draft_instruction.save()

    if ToolInstruction.objects.filter(instruction=draft_instruction, tool=tool).exists():
        return Response({'error': 'Инструмент уже добавлен в инструкцию'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        tool_instruction = ToolInstruction.objects.create(
            instruction=draft_instruction,
            tool=tool,
            tool_parameter=None,
        )
    except Exception as e:
        return Response({'error': f'Ошибка при создании связи: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = InstructionSerializer(draft_instruction)
    return Response(serializer.get_tools(draft_instruction), status=status.HTTP_200_OK)


@api_view(["GET"])
def get_instructions_list(request):
    status_param = request.GET.get("status", '')
    submit_date_start = request.GET.get("submit_date_start")
    submit_date_end = request.GET.get("submit_date_end")

    instructions = Instruction.objects.exclude(status__in=['draft', 'deleted'])

    if status_param in ['submitted', 'completed', 'rejected']:
        instructions = instructions.filter(status=status_param)

    if submit_date_start and parse_datetime(submit_date_start):
        instructions = instructions.filter(
            submit_date__gte=parse_datetime(submit_date_start))

    if submit_date_end and parse_datetime(submit_date_end):
        instructions = instructions.filter(
            submit_date__lt=parse_datetime(submit_date_end))

    serializer = InstructionSerializer(instructions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_instruction_by_id(request, instruction_id):
    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    serializer = InstructionSerializer(instruction, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_instruction(request, instruction_id):
    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    allowed_fields = ['submit_date', 'intent']

    data = {key: value for key, value in request.data.items()
            if key in allowed_fields}

    if not data:
        return Response({"error": "Нет данных для обновления или поля не разрешены"},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = InstructionSerializer(instruction, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_status_user(request, instruction_id):
    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    if instruction.status != 'draft':
        return Response({"error": "Инструкцию нельзя изменить, так как она не в статусе 'Черновик'"},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    required_fields = ['intent']

    missing_fields = [
        field for field in required_fields if not getattr(instruction, field)]

    if missing_fields:
        return Response(
            {"error": f"Не заполнены обязательные поля: {
                ', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    instruction.status = 'submitted'
    instruction.submit_date = timezone.now()
    instruction.save()

    serializer = InstructionSerializer(instruction, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_status_admin(request, instruction_id):
    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in ['completed', 'rejected']:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if instruction.status != 'submitted':
        return Response({'error': "Инструкция ещё не сформирована"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    instruction.status = request_status
    instruction.moderator = get_moderator()
    instruction.complete_date = timezone.now()
    instruction.save()

    serializer = InstructionSerializer(instruction, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_instruction(request, instruction_id):
    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    if instruction.status != 'draft':
        return Response({'error': 'Нельзя удалить данную инструкцию'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    instruction.status = 'deleted'
    instruction.save()
    serializer = InstructionSerializer(instruction, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_tool_from_instruction(request, tool_id, instruction_id):
    try:
        tool_instruction = ToolInstruction.objects.get(
            tool_id=tool_id, instruction_id=instruction_id)
    except ToolInstruction.DoesNotExist:
        return Response({"error": "Связь между инструментом и инструкцией не найдена"}, status=status.HTTP_404_NOT_FOUND)

    tool_instruction.delete()

    try:
        instruction = Instruction.objects.get(pk=instruction_id)
    except Instruction.DoesNotExist:
        return Response({"error": "Инструкция не найдена после удаления инструмента"}, status=status.HTTP_404_NOT_FOUND)

    serializer = InstructionSerializer(instruction, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_tool_instruction(request, tool_id, instruction_id):
    try:
        tool_instruction = ToolInstruction.objects.get(
            tool_id=tool_id, instruction_id=instruction_id)
    except ToolInstruction.DoesNotExist:
        return Response({"error": "Связь между инструментом и инструкцией не найдена"}, status=status.HTTP_404_NOT_FOUND)

    # Обновляем параметр инструмента
    tool_instruction.tool_parameter = request.data.get(
        'tool_parameter', tool_instruction.tool_parameter)
    tool_instruction.save()

    # Возвращаем обновлённые данные
    serializer = ToolInstructionSerializer(tool_instruction)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({"error": "Некорректные данные"}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(
        user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)
