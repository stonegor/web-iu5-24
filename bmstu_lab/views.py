from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Instruction, Tool, ToolInstruction
from django.db import connection


def get_tools(request):

    try:
        instruction = Instruction.objects.get(
            user=request.user, status='draft')
    except Instruction.DoesNotExist:
        instruction = None

    query = request.GET.get('tool', '')
    if query:
        tools = Tool.objects.filter(title__icontains=query, status='active')
    else:
        tools = Tool.objects.filter(status='active')

    instructions_count = ToolInstruction.objects.filter(
        instruction=instruction).count()

    return render(request, 'tools.html', {
        'tools': tools,
        'instructions_count': instructions_count,
        'instruction_id': instruction.id if instruction else None,
        'query': query
    })


def add_to_instruction(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id, status='active')
    user = request.user

    instruction, created = Instruction.objects.get_or_create(
        user=user, status='draft', defaults={'intent': 'Пустое текст запроса'})
    tool_instruction, created = ToolInstruction.objects.get_or_create(instruction=instruction, tool=tool, defaults={
        'tool_parameter': ''
    })

    if not created:
        tool_instruction.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


def view_instruction(request, instruction_id):
    instruction = get_object_or_404(
        Instruction, id=instruction_id, user=request.user, status='draft')

    tools_in_instruction = ToolInstruction.objects.filter(
        instruction=instruction).select_related('tool').order_by('id')

    return render(request, 'instruction.html', {
        'instruction': instruction,
        'tools_in_instruction': tools_in_instruction
    })


def get_tool_detail(request, id):
    tool = get_object_or_404(Tool, id=id, status='active')
    return render(request, 'tool.html', {'tool': tool})


def delete_instruction(request, instruction_id):

    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE instruction
            SET status = %s
            WHERE id = %s
        """, ['deleted', instruction_id])

    return redirect('tools')
