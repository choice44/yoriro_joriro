from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from recruitments.models import Recruitments, Applicant

from recruitments.serializers import (
    RecruitmentSerializer,
    RecruitmentDetailSerializer,
)


class RecruitmentView(APIView):
    def get(self, request):
        recruitments = Recruitments.objects.all()
        serializer = RecruitmentSerializer(recruitments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RecruitmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        return Response(({"message":"동료 모집 작성 완료"}, serializer.data), status=status.HTTP_200_OK)


class RecruitmentDetailView(APIView):
    def get(self, request, recruitment_id):
        recruitments = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentDetailSerializer(recruitments)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, recruitment_id):
        pass
    
    def delete(self, request, recruitment_id):
        pass


class RecruitmentJoinView(APIView):
    def get(self, request, recruitment_id):
        pass

    def post(self, request, recruitment_id):
        pass
