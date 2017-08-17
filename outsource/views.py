from django.shortcuts import render
from outsource.models import *

from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from outsource.serializers import DeviceSerializer

@csrf_exempt
def payment(request):
    price=4000
    name="오레오 초코쉐이크"
    if request.method=="POST":
        if not request.POST.get('price')==None:
            price=request.POST.get('price')

        if not request.POST.get('name') == None:
            name = request.POST.get('name')

    return render(request,'payment.html', {'price':price, 'name':name})

def payment_complete(request):
    return render(request,'payment_complete.html')

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = MyDevice.objects.all()
    serializer_class = DeviceSerializer