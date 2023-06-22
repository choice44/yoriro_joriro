from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework import status, permissions

from recruitments.models import Recruitments, Applicant
from recruitments.serializers import (
    RecruitmentSerializer,
    RecruitmentDetailSerializer,
    RecruitmentEditSerializer,
    RecruitmentJoinSerializer
)

from datetime import datetime


class RecruitmentView(ListAPIView):
    queryset = Recruitments.objects.all().order_by("-created_at")
    serializer_class = RecruitmentSerializer

    def get_serializer_context(self):
        return {
            'request': None,  # None이 아닌 경우에 full url 표시
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request):
        recruitment = Recruitments.objects.all()

        now_time = datetime.now()
        for obj in recruitment:
            if now_time >= obj.arrival:
                obj.is_complete = 3
                obj.save()
            elif now_time >= obj.departure:
                obj.is_complete = 2
                obj.save()

        response = self.list(request)
        return Response(response.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RecruitmentSerializer(data=request.data)
        if serializer.is_valid():
            recruitment = serializer.save(user=request.user)
            recruitment.participant.add(request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(({"message": "동료 모집 작성 완료"}), status=status.HTTP_201_CREATED)


class RecruitmentDetailView(APIView):

    def get(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentDetailSerializer(recruitment)

        now_time = datetime.now()

        if now_time >= recruitment.arrival:
            recruitment.is_complete = 3
            recruitment.save()
        elif now_time >= recruitment.departure:
            recruitment.is_complete = 2
            recruitment.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentEditSerializer(
            recruitment, data=request.data, partial=True)
        if recruitment.user == request.user:
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(({"message": "동료 모집 수정 완료"}), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        if recruitment.user == request.user:
            recruitment.delete()
            return Response({"message": "동료 모집 삭제 완료"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class RecruitmentJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recruitment_id):
        applicant = Applicant.objects.filter(recruitment_id=recruitment_id)
        serializer = RecruitmentJoinSerializer(applicant, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentJoinSerializer(data=request.data)

        if recruitment.is_complete != 0:
            return Response({"message": "마감된 지원입니다."}, status=status.HTTP_204_NO_CONTENT)
        if Applicant.objects.filter(recruitment=recruitment, user=request.user).exists() or request.user in recruitment.participant.all():
            return Response({"message": "이미 지원하였습니다."}, status=status.HTTP_204_NO_CONTENT)

        if serializer.is_valid():
            serializer.save(recruitment=recruitment, user=request.user)
            return Response({"message": "참가 신청 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class ApplicantDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, applicant_id):
        applicant = get_object_or_404(Applicant, id=applicant_id)
        serializer = RecruitmentJoinSerializer(applicant, data=request.data)
        if applicant.user == request.user:
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message": "지원 수정 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, applicant_id):
        applicant = get_object_or_404(Applicant, id=applicant_id)
        if applicant.user == request.user:
            applicant.delete()
            return Response({"message": "지원 삭제 완료"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class ApplicantAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, applicant_id):
        applicant = get_object_or_404(Applicant, id=applicant_id)
        recruitment = get_object_or_404(
            Recruitments, id=applicant.recruitment_id)

        if recruitment.user == request.user:
            if applicant.acceptence != 0:
                return Response({"message": "이전에 처리한 지원자입니다."}, status=status.HTTP_208_ALREADY_REPORTED)

            if recruitment.is_complete != 0:
                return Response({"message": "더이상 수락할수 없습니다."}, status=status.HTTP_208_ALREADY_REPORTED)

            applicant.acceptence = 2
            applicant.save()
            recruitment.participant.add(applicant.user)

            if recruitment.participant.count() >= recruitment.participant_max:
                recruitment.is_complete = 1
                recruitment.save()
            return Response({"message": "참가 수락 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class ApplicantRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, applicant_id):
        applicant = get_object_or_404(Applicant, id=applicant_id)
        recruitment = get_object_or_404(
            Recruitments, id=applicant.recruitment_id)

        if recruitment.user == request.user:
            if applicant.acceptence != 0:
                return Response({"message": "이전에 처리한 지원자입니다."}, status=status.HTTP_204_NO_CONTENT)

            applicant.acceptence = 1
            applicant.save()
            return Response({"message": "참가 거절 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
