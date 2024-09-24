from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_tools),
    path('tool/<int:id>/', views.get_tool, name='tool_url'),
    path('tools/', views.get_tools, name='tools'),
    path('cart/', views.get_orders, name='cart')
]
