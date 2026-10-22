from django.urls import path
from .views import TaskView, TaskDetailView, GroupedTaskView

urlpatterns = [
    path('', TaskView.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('grouped/',GroupedTaskView.as_view(), name='task-grouped'),
]
