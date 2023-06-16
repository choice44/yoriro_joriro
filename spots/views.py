from rest_framework import permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from spots.models import Area, Sigungu, Spot
from spots.serializers import AreaSerializer, SigunguSerializer, SpotSerializer


class AreaView(APIView):
    def get(self, request):
        areas = Area.objects.all()
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SigunguView(APIView):
    def get(self, request, area_id):
        sigungus = Sigungu.objects.filter(area=area_id).all()
        serializer = SigunguSerializer(sigungus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class SpotListView(APIView):
#     def get(self, request):
#         spots = Spot.objects.all()
#         serializer = SpotSerializer(spots, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class SpotFilterView(ListAPIView):
    queryset = Spot.objects.all().order_by("id")
    serializer_class = SpotSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["type", "area", "sigungu",]
    search_fields = ['title',]


class SpotDetailView(APIView):
    def get(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        serializer = SpotSerializer(spot)
        return Response(serializer.data, status=status.HTTP_200_OK)
