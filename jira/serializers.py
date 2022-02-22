from rest_framework import serializers, exceptions
from .models import AppImage, User


class AppImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppImage
        fields = (
            'id',
            'width',
            'height',
            'img',
            'desc',
        )
        read_only_fields = (
            'id',
            'width',
            'height',
        )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5, max_length=20, required=True)
    avatar_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(max_length=191, write_only=True)
    avatar = AppImageSerializer(read_only=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        user_tmp = User.objects.filter(username__iexact=username).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '用户名已注册！'})

        avatar = None
        avatar_id = validated_data.get('avatar_id')
        if avatar_id:
            try:
                avatar = AppImage.objects.get(pk=avatar_id)
            except AppImage.DoesNotExist:
                raise serializers.ValidationError({'msg': f'avatar_id = {avatar_id} does not exist!'})

        phone_number = validated_data['phone_number']
        user_tmp = User.objects.filter(phone_number=phone_number).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '手机号已注册!'})

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', None),
            first_name=validated_data['first_name'],
            phone_number=validated_data['phone_number'],
            avatar=avatar,
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'phone_number',
            'avatar_id',
            'avatar',
            'password',
        )
        read_only_fields = (
            'id',
            'avatar',
        )
