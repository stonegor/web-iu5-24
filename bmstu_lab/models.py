from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


class Instruction(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('submitted', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')
    creation_time = models.DateTimeField(default=timezone.now)
    submit_date = models.DateTimeField(blank=True, null=True)
    complete_date = models.DateTimeField(blank=True, null=True)
    moderator = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='instruction_user_set', blank=True, null=True)
    intent = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instruction'

    def __str__(self):
        return f"Instruction {self.id} - {self.status}"


class Tool(models.Model):
    title = models.CharField(unique=True, max_length=50)
    description = models.TextField()
    description_detail = models.TextField()
    status = models.CharField(max_length=20, choices=[(
        'active', 'Действует'), ('deleted', 'Удалён')], default='active')
    image_url = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tool'

    def __str__(self):
        return self.title


class ToolInstruction(models.Model):
    tool = models.ForeignKey(
        Tool, on_delete=models.CASCADE, blank=True, null=True)
    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, blank=True, null=True)
    tool_parameter = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tool_instruction'

    def __str__(self):
        return f"Tool \"{self.tool.title}\" (Parameter: {self.tool_parameter} in Instruction {self.instruction.id})"
