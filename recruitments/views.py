from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from recruitments.models import Recruitments, Applicant, Participant


class RecruitmentView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class RecruitmentDetailView(APIView):
    def get(self, request):
        pass


class RecruitmentJoinView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass
