from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "max_length": 5,
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data: dict) -> get_user_model():
        return get_user_model().objects.create_user(**validated_data)

    def update(
            self, instance: get_user_model(),
            validated_data: dict
    ) -> get_user_model():
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            with transaction.atomic():
                user.set_password(password)
                user.save()

        return user
