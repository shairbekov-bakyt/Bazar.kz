from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user.models import CustomUser as User
from user.utils import Util
from user.selectors import get_user_by_email


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password, ])


class ChangeUserInfoSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(
        required=False, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["last_name", "first_name", "email", "phone_number", "old_password", "new_password"]

    def validate(self, attrs):
        if not attrs.get('old_password'):
            return attrs

        user = get_user_by_email(attrs['email'])

        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {"old_password": "old_password is invalid"}
            )

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        return super().update(instance, validated_data)


class ForgotPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, validators=[validate_password])
    new_password = serializers.CharField(required=True, validators=[validate_password])


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token["username"] = user.email
        return token

    def validate(self, attrs):
        data = super(MyTokenObtainPairSerializer, self).validate(attrs)
        user = get_user_by_email(attrs["email"])
        data["is_superuser"] = user.is_superuser
        data["user_id"] = user.id
        data["first_name"] = user.first_name
        data["last_name"] = user.last_name
        data["phone_number"] = str(user.phone_number)
        data["email"] = user.email
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="email уже занят")
        ],
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    policy_agreement = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = User
        fields = (
            "id",
            "last_name",
            "first_name",
            "email",
            "phone_number",
            "password",
            "password2",
            "policy_agreement",
        )

        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        if not attrs["policy_agreement"]:
            raise serializers.ValidationError(
                {"policy_agreement": "policy agreement must be True"}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            activation_code=Util.get_random_string(12)
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class VerifyEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    code = serializers.CharField(max_length=13)

    def validate(self, attrs):
        activation_code = User.objects.get(email=dict(attrs)['email'])

        if activation_code.activation_code != dict(attrs)['code']:
            raise ValueError("code is invalid")

        activation_code.is_active = True
        activation_code.save()
        return attrs

    def create(self, validated_data):
        return {"status": "activate"}
