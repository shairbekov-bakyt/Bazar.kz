from django.http import HttpRequest

import django_filters
from rest_framework import status, filters
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from advert.serializers import advert_serializers as serializers
from advert.models import Advert, AdvertImage, City, AdvertContact

from advert.serializers import permissions
from phonenumber_field.validators import validate_international_phonenumber


class AdvertFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="start_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="start_price", lookup_expr="lte")
    image = django_filters.BooleanFilter(
        lookup_expr="isnull", field_name="advert_image"
    )

    class Meta:
        model = Advert
        fields = ["min_price", "max_price", "image", "city", "category", "sub_category"]


class CityListView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer


class AdvertViewSet(ModelViewSet):
    queryset = Advert.objects.filter(status="act")
    serializer_class = serializers.AdvertCreateSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter, filters.SearchFilter,
    ]
    permission_classes = [permissions.IsOwnerOrReadOnly]
    filterset_class = AdvertFilter
    ordering_fields = ["created_date", "end_price"]
    ordering = ["created_date"]
    search_fields = ["name"]

    def create(self, request, *args, **kwargs):
        imgs = request.FILES.getlist("image")
        if len(imgs) > 8:
            raise serializers.ValidationError("Максимальное кол-во изображений: 8")

        contacts = request.data.getlist("advert_contact")

        if len(imgs) > 8:
            raise serializers.ValidationError("Максимальное кол-во контактов: 8")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        advert = serializer.save()

        img_objects = []
        for img in imgs:
            img_objects.append(AdvertImage(advert=advert, image=img))

        AdvertImage.objects.bulk_create(img_objects)

        ad_contacts = []
        for contact in contacts[0].split(','):
            validate_international_phonenumber(contact)
            ad_contacts.append(AdvertContact(advert=advert, phone_number=contact))

        AdvertContact.objects.bulk_create(ad_contacts)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AdvertListSerializer
        if self.action == 'retrieve':
            return serializers.AdvertDetailSerializer
        return super().get_serializer_class()


class PremiumAdvertView(ListAPIView):
    queryset = Advert.objects.filter(status="act", promote__isnull=False)
    serializer_class = serializers.AdvertListSerializer


