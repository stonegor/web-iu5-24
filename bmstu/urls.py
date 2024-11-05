from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from bmstu_lab import views
from bmstu_lab.views import *
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('api/tools/', get_tools_list, name='get_tools_list'),  # GET
    path('api/tools/<int:tool_id>/', get_tool_by_id,
         name='get_tool_by_id'),  # GET
    path('api/tools/create/', create_tool, name='create_tool'),  # POST
    path('api/tools/<int:tool_id>/update/',
         update_tool, name='update_tool'),  # PUT
    path('api/tools/<int:tool_id>/delete/',
         delete_tool, name='delete_tool'),  # DELETE
    path('api/tools/<int:tool_id>/update_image/',
         update_tool_image, name='update_image'),  # POST
    path('api/tools/<int:tool_id>/add_tool_to_instruction/',
         add_tool_to_instruction, name='add_tool_to_instruction'),  # POST

    # Set of methods for instructions
    path('api/instructions/', get_instructions_list,
         name='get_instructions_list'),  # GET
    path('api/instructions/<int:instruction_id>/',
         get_instruction_by_id, name='get_instruction_by_id'),  # GET
    path('api/instructions/<int:instruction_id>/update/',
         update_instruction, name='update_instruction'),  # PUT
    path('api/instructions/<int:instruction_id>/update_status_user/',
         update_status_user, name='update_status_user'),  # PUT
    path('api/instructions/<int:instruction_id>/update_status_admin/',
         update_status_admin, name='update_status_admin'),  # PUT
    path('api/instructions/<int:instruction_id>/delete/',
         delete_instruction, name='delete_instruction'),  # DELETE

    # Set of methods for many-to-many relationship
    path('api/tool/<int:tool_id>/instruction/<int:instruction_id>/update_tool_instruction/',
         update_tool_instruction, name='update_tool_instruction'),  # PUT
    path('api/tool/<int:tool_id>/instruction/<int:instruction_id>/delete_tool_instruction/',
         delete_tool_from_instruction, name='delete_tool_instruction'),  # DELETE

    # Set of methods for users
    path('api/users/register/', register, name='register'),  # POST
    path('api/users/login/', login, name='login'),  # POST
    path('api/users/logout/', logout, name='logout'),  # POST
    path('api/users/<int:user_id>/update/',
         update_user, name='update_user'),  # PUT
]
