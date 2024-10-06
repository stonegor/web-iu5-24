from django.shortcuts import render
from bmstu_lab.data import tools_data, instructions_data, tool_instruction
from django.http import HttpResponse


def get_tools(request):

    query = request.GET.get('tool', '')
    filtered_tools = [tool for tool in tools_data
                      if query.lower() in tool['title'].lower()]

    id = 1
    user_instruction = next(
        (instruction for instruction in instructions_data if instruction['id'] == id), None)

    instructions = [
        tools_data[tool['tool_id']] for tool in tool_instruction if tool['instruction_id'] == user_instruction['id']
    ]

    instructions_count = len(instructions)

    return render(request, 'tools.html', {'data': {'tools': filtered_tools, 'instructions_count': instructions_count}})


def get_instructions(request, id):

    user_instruction = next(
        (instruction for instruction in instructions_data if instruction['id'] == id), None)

    if not user_instruction:
        return HttpResponse('Корзина пользователя не найдена', status=404)

    instructions = [
        tools_data[tool['tool_id']] for tool in tool_instruction if tool['instruction_id'] == user_instruction['id']
    ]
    return render(request, 'instruction.html', {'data': {'instructions': instructions, 'intent': user_instructions['intent']}})


def get_tool(request, id):
    tool = next((tool for tool in tools_data if tool['id'] == id), None)
    if not tool:
        return HttpResponse('Инструмент не найден', status=404)
    return render(request, 'tool.html', {'data': {
        'tool': tool
    }})
