from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_tools, name='tools'),
    path('tool/<int:tool_id>/add/',
         views.add_to_instruction, name='add_to_instruction'),
    path('instruction/<int:instruction_id>/',
         views.view_instruction, name='instruction'),
    path('tool/<int:id>/', views.get_tool_detail, name='tool_url'),
    path('instruction/<int:instruction_id>/delete/',
         views.delete_instruction, name='delete_instruction'),
]
