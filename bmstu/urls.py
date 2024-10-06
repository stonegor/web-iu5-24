from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('tool/<int:id>/', views.get_tool, name='tool_url'),
    path('tools/', views.get_tools, name='tools'),
    path('instruction/<int:id>', views.get_instructions, name='instruction')
]
