from rest_framework import serializers
from outsource.models import *

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyDevice
        fields = ('dev_id','reg_id','name','is_active', 'user')

class BeverageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Beverage
        fields = ('name', 'image', 'price', 'pk')

class CafeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cafe
        fields = ('cafe_image','locationString', 'name', 'pk','is_open')

class CouponSerializer(serializers.HyperlinkedModelSerializer):
    cafe = CafeSerializer()
    class Meta:
        model=Coupon
        fields = ('pk', 'coupon_progress', 'cafe')

class CafeFullSerializer(serializers.HyperlinkedModelSerializer):
    beverages = BeverageSerializer(many=True)
    class Meta:
        model = Cafe
        fields = ('cafe_image','locationString', 'name', 'pk','beverages','is_open')

class UserManageSerializer(serializers.HyperlinkedModelSerializer):
    def create(self,validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        instance.email = validated_data.get('email',instance.email)
        instance.birth_year = validated_data.get('birth_year',instance.birth_year)
        instance.birth_month = validated_data.get('birth_month',instance.birth_month)
        instance.birth_day = validated_data.get('birth_day',instance.birth_day)
        instance.gender = validated_data.get('gender',instance.gender)

        if not validated_data.get('password') == None :
            instance.set_password(validated_data.get('password', instance.password))

        instance.save()
        return instance
    class Meta:
        model = User
        fields = ('username','birth_year', 'birth_month', 'birth_day', 'password',
                  'gender','name','phone_number','email','profile_picture')

class BeverageOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BeverageOption
        fields = ('beverage_id', 'whipping_cream', 'is_ice', 'size','shot_num')

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    orderer_username = serializers.SerializerMethodField('GetOrdererUserName')
    options = BeverageOptionSerializer(many=True,read_only=True)

    def GetOrdererUserName(self, instance):
        return instance.orderer.username

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

    class Meta:
        model=Order
        fields = ( 'pk', 'order_time','payment_type', 'orderer_username', 'options', 'amount_price')
        read_only_fields = ('order_time','orderer_username')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    beverages = BeverageSerializer(many=True,read_only=True)
    def create(self, validated_data):
        return Event.objects.create(**validated_data)

    class Meta:
        model = Event
        fields = ('pk','event_type','price', 'to_time', 'from_time','beverages')
