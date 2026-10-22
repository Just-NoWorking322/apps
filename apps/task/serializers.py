from rest_framework import serializers
from .models import Task
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description")
        read_only_fields = ("id",)
        def get_time_left(self, object):
            if not object.deadline:
                return "Дедлайн не указан"

            if object.is_completed:
                return "Задача выполнена"

            remaining = object.deadline - timezone.now()

            if remaining.total_seconds() <= 0:
                return "Дедлайн просрочен"

            days = remaining.days
            hours = remaining.seconds // 3600

            if days:
                return f"{days} days left"

            return f"{hours} hours left"

    # Валидация поля title
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Минимум 3 символа в названии!")
        return value.strip()
