from django.urls import path

from .views import TodoListCreateView, TodoDetails

app_name = 'todo'

urlpatterns = [
    path('', TodoListCreateView.as_view(), name='list_create_todo'),
    path('<int:id>', TodoDetails.as_view(), name='todo_detail'),
]
