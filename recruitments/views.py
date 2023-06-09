from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from recruitments.models import Recruitments, Applicant

from recruitments.serializers import (
    RecruitmentSerializer,
    RecruitmentDetailSerializer,
    RecruitmentEditSerializer,
    RecruitmentJoinSerializer
)


class RecruitmentView(APIView):
    def get(self, request):
        recruitment = Recruitments.objects.all()
        serializer = RecruitmentSerializer(recruitment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RecruitmentSerializer(data=request.data)
        if serializer.is_valid():
            recruitment = serializer.save(user=request.user)
            recruitment.participant.add(request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(({"message":"동료 모집 작성 완료"}), status=status.HTTP_201_CREATED)


class RecruitmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentDetailSerializer(recruitment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentEditSerializer(recruitment, data=request.data, partial=True)
        if recruitment.user == request.user:
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(({"message":"동료 모집 수정 완료"}), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        if recruitment.user == request.user:
            recruitment.delete()
            return Response({"message":"동료 모집 삭제 완료"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class RecruitmentJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recruitment_id):
        applicant = Applicant.objects.filter(recruitment_id=recruitment_id)
        serializer = RecruitmentJoinSerializer(applicant, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, recruitment_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        serializer = RecruitmentJoinSerializer(data=request.data)
        if Applicant.objects.filter(recruitment=recruitment, user=request.user).exists() or request.user in recruitment.participant.all():
            return Response({"message":"이미 지원하였습니다."}, status=status.HTTP_204_NO_CONTENT)
        
        if serializer.is_valid():
            serializer.save(recruitment=recruitment, user=request.user)
            return Response({"message":"참가 신청 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class ApplicantAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 고민을 정말 많이 했는데 직접 수정하는 부분을 입력 받는게 아니긴 한데 수정하는 부분이 있으어서 put로 했습니다만 아직 정확하게 모르겠네요...
    def put(self, request, recruitment_id, applicant_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        if  recruitment.user == request.user:
            applicant = get_object_or_404(Applicant, id=applicant_id)
            applicant.save()
            if applicant.user in recruitment.participant.all():
                return Response({"message":"이미 수락하였습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:            
                applicant.acceptence=2
                applicant.save()
                recruitment.participant.add(applicant.user)
                return Response({"message":"참가 수락 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


class ApplicantRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, recruitment_id, applicant_id):
        recruitment = get_object_or_404(Recruitments, id=recruitment_id)
        if  recruitment.user == request.user:
            applicant = get_object_or_404(Applicant, id=applicant_id)
            applicant.save()
            if applicant.user in recruitment.participant.all():
                return Response({"message":"이미 수락하였습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:            
                applicant.acceptence=1
                applicant.save()
                return Response({"message":"참가 거절 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


# class ApplicantAcceptenceView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, recruitment_id, applicant_id):
#         recruitment = get_object_or_404(Recruitments, id=recruitment_id)
#         if  recruitment.user == request.user:
#             applicant = get_object_or_404(Applicant, id=applicant_id)
#             applicant.save()
#             if applicant.user in recruitment.participant.all():
#                 return Response({"message":"이미 수락하였습니다."}, status=status.HTTP_204_NO_CONTENT)
#             else:            
#                 applicant.acceptence = True
#                 recruitment.participant.add(applicant.user)
#                 applicant.delete()
#                 return Response({"message":"참가 수락 완료"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)

#     def delete(self, request, recruitment_id, applicant_id):
#         recruitment = get_object_or_404(Recruitments, id=recruitment_id)
#         if  recruitment.user == request.user:            
#             applicant = get_object_or_404(Applicant, id=applicant_id)
#             applicant.delete()
#             return Response({"message":"참가 거절 완료"}, status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response({"message":"권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
        
        