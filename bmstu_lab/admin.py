from django.contrib import admin
from .models import Instruction, Tool, ToolInstruction


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'creation_time',
                    'submit_date', 'complete_date', 'moderator', 'user')
    list_filter = ('status', 'creation_time', 'submit_date', 'complete_date')
    search_fields = ('id', 'intent')
    date_hierarchy = 'creation_time'
    ordering = ('-creation_time',)
    autocomplete_fields = ('moderator', 'user')


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'image_url')
    list_filter = ('status',)
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(ToolInstruction)
class ToolInstructionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tool', 'instruction', 'tool_parameter')
    search_fields = ('tool__title', 'instruction__id')
    autocomplete_fields = ('tool', 'instruction')
