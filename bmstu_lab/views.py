from django.shortcuts import render
from bmstu_lab.data import tools_data, orders_data
from django.http import HttpResponse


def get_tools(request):

    query = request.GET.get('tool', '')
    filtered_tools = [tool for tool in tools_data
                      if query.lower() in tool['title'].lower()]

    user_id = 1
    user_orders = next(
        (cart for cart in orders_data if cart['id'] == user_id), None)

    orders_count = len(user_orders)

    return render(request, 'index.html', {'data': {'tools': filtered_tools, 'orders_count': orders_count}})


def get_orders(request):

    user_id = 1
    user_orders = next(
        (cart for cart in orders_data if cart['id'] == user_id), None)

    if not user_orders:
        return HttpResponse('Корзина пользователя не найдена', status=404)

    orders = [
        tool for tool in tools_data if tool['id'] in user_orders['tools']
    ]
    return render(request, 'orders.html', {'data': {'orders': orders}})


def get_tool(request, id):
    tool = next((tool for tool in tools_data if tool['id'] == id), None)
    if not tool:
        return HttpResponse('Инструмент не найден', status=404)
    return render(request, 'tool.html', {'data': {
        'tool': tool
    }})
