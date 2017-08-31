from django.db import models
from django.contrib.auth.models import (BaseUserManager,AbstractBaseUser)
from django.conf import settings
from fcm.models import AbstractDevice

# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(self,username,password=None):
        user=self.model(
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,password=None):
        user=self.create_user(
            username=username,
            password=password
        )
        user.is_admin=True
        user.is_superuser=True
        user.is_active = True
        user.save(using=self._db)

        return user

class TimeStampedModel(models.Model):
	created_time = models.DateTimeField(auto_now_add=True)
	modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		abstract=True

class BaseUser(AbstractBaseUser, TimeStampedModel):
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=15, default="")
    email=models.CharField(max_length=50, default="")
    USER_TYPE_CHOICE = (
        (0, '유저'),
        (1, '카페'),
    )

    user_type=models.IntegerField(choices=USER_TYPE_CHOICE, default=0)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = AccountManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return "username: " + self.username

    @property
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return self.is_admin

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return self.is_admin

    def get_short_name(self):
        return self.name

class MyDevice(AbstractDevice):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='device')

def user_directory_path(instance, filename):
    return 'user/{0}/{1}'.format(instance.username, filename)
class User(BaseUser):
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True)
    birth_year = models.IntegerField(default=1998)
    birth_month = models.IntegerField(default=8)
    birth_day = models.IntegerField(default=18)
    gender = models.BooleanField(default=True)
    favorite_cafe=models.ManyToManyField('Cafe', blank=True)

def cafe_directory_path(instance, filename):
    return 'cafe/{0}/profile/{1}'.format(instance.username, filename)
class Cafe(BaseUser):
    cafe_image = models.ImageField(upload_to=cafe_directory_path, null=True)
    locationX=models.FloatField()
    locationY = models.FloatField()
    locationString=models.CharField(max_length=50)
    current_order_num=models.IntegerField(default=0)
    is_open=models.BooleanField(default=False)
    can_use_coupon=models.BooleanField(default=True)

def beverage_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    return 'cafe/{0}/menu/{1}'.format(instance.cafe.username, instance.name+'.'+ext)

class Beverage(models.Model):
    cafe=models.ForeignKey(Cafe, related_name="beverages")
    name=models.CharField(max_length=30)
    image = models.ImageField(upload_to=beverage_directory_path, null=True)
    price=models.CharField(max_length=50)
    coupon_payment=models.BooleanField(default=False)

    def __str__(self):
        return self.cafe.locationString+" "+self.cafe.name+"의 "+self.name

class Order(models.Model):
    order_time=models.DateTimeField(auto_now_add=True)
    orderer=models.ForeignKey(User,related_name='orders')
    cafe = models.ForeignKey(Cafe,related_name="orders")
    is_done=models.BooleanField(default=False)
    order_num=models.IntegerField(default=0)
    options=models.ManyToManyField('BeverageOption')
    PAYMENT_TYPE_CHOICE = (
        (0, '일반결제'),
        (1, '쿠폰결제'),
        (2, '이벤트결제')
    )
    amount_price=models.IntegerField(default=0)
    payment_type=models.IntegerField(default=0,choices=PAYMENT_TYPE_CHOICE)

    def __str__(self):
        if self.options.count()>1 :
            return self.orderer.username + "->" + self.cafe.name + "(" + self.options.first().beverage.name + " 및"+str(self.options.count()-1)+" 개)"
        else :
            if self.options.count()==0 :
                return self.orderer.username + "->" + self.cafe.name

            return self.orderer.username + "->" + self.cafe.name+"("+self.options.first().beverage.name+")"

class Coupon(models.Model):
    last_coupon_update=models.DateTimeField(auto_now_add=True)
    cafe = models.ForeignKey(Cafe, related_name="coupons")
    user = models.ForeignKey(User, related_name="coupons")
    coupon_progress=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + "의 " + self.cafe.name + "쿠폰 : " + str(self.coupon_progress)

class Event(models.Model):
    cafe=models.ForeignKey(Cafe, related_name='events')
    beverages=models.ManyToManyField(Beverage,related_name='events', blank=True)
    EVENT_TYPE_CHOICE=(
        (0, '가격할인'),
        (1, '쿠폰추가')
    )
    event_type = models.IntegerField(default=0, choices=EVENT_TYPE_CHOICE)
    price=models.IntegerField(default=0)

    to_time=models.DateTimeField()
    from_time = models.DateTimeField()

    def __str__(self):
        return self.cafe.name + "의 이벤트"

class BeverageOption(models.Model):
    beverage = models.ForeignKey(Beverage)
    whipping_cream=models.BooleanField(default=False)
    is_ice = models.BooleanField(default=False)
    size=models.IntegerField(default=0)
    shot_num=models.IntegerField(default=0)

