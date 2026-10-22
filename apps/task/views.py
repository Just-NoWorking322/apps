from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
from django.utils import timezone

from .models import Task
from .serializers import TaskSerializer


class TaskView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 1. Проверяем, есть ли данные в кэше
        tasks_data = cache.get("tasks")

        # Если данные есть в кэше — возвращаем их
        if tasks_data is not None:
            return Response(tasks_data)

        # 2. Если данных нет в кэше — берем из базы данных
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        tasks_data = serializer.data

        # 3. Сохраняем в кэш на 60 секунд
        cache.set("tasks", tasks_data, 60)

        return Response(tasks_data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 4. Очищаем кэш при создании новой задачи
        cache.delete("tasks")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Очищаем кэш при обновлении задачи
        cache.delete("tasks")
        return Response(serializer.data)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()

        # Очищаем кэш при удалении задачи
        cache.delete("tasks")
        return Response({"message": "Задача удалена"}, status=status.HTTP_204_NO_CONTENT)
    
class GroupedTaskView(APIView):
    def get(self, request):
        tasks = Task.objects.exclude(
            deadline__isnull=True
        ).order_by("deadline")

        grouped = defaultdict(list)

        for task in tasks:
            date_key = timezone.localtime(
                task.deadline
            ).date().isoformat()

            grouped[date_key].append(task)

        result = {
            date: TaskSerializer(
                items,
                many=True,
                context={"request": request},
            ).data
            for date, items in grouped.items()
        }

        return Response(result)