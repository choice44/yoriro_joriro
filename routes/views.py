from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from routes.models import Route, Comment, RouteRate, Spot
from routes.serializers import (
    RouteSerializer,
    RouteCreateSerializer,
    RouteDetailSerializer,
    SpotSerializer,
    CommentSerializer,
    CommentCreateSerializer
)

class RouteView(APIView):
    # 로그인한 사람은 여행루트 작성 가능. 아니면 여행루트 전체 목록 조회만 가능.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 여행루트 조회
    def get(self, request):
        routes = Route.objects.all().order_by("-created_at")
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 여행루트 작성
    def post(self, request):
        serializer = RouteCreateSerializer(data=request.data)
        
        if not request.user.is_authenticated:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(user=request.user)

        return Response(({"message": "여행 루트 작성 완료!"},serializer.data), status=status.HTTP_201_CREATED)


class SpotCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SpotSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(({"message": "스팟 등록 완료!"},serializer.data), status=status.HTTP_201_CREATED)


class RouteDetailView(APIView):
    # 로그인한 사람은 여행루트 수정/삭제 가능. 아니면 여행루트 상세보기만 가능.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 여행루트 상세보기
    def get(self, request, route_id):
        route = get_object_or_404(Route, id=route_id)
        serializer = RouteDetailSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 여행루트 수정하기
    def put(self, request, route_id):
        route = get_object_or_404(Route, id=route_id)
        serializer = RouteCreateSerializer(route, data=request.data)

        if route.user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(user=request.user)

        return Response(({"message": "여행 루트 수정 완료!"},serializer.data), status=status.HTTP_200_OK)

            
    # 여행루트 삭제하기
    def delete(self, request, route_id):
        route = get_object_or_404(Route, id=route_id)
        
        if route.user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        route.delete()
        return Response({"message": "여행 루트 삭제 완료!"}, status=status.HTTP_204_NO_CONTENT)
            


class CommentView(APIView):
    # 로그인한 사람은 댓글 작성 가능. 아니면 댓글 조회만 가능.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 댓글 전체 조회
    def get(self, request, route_id):
        routes = get_object_or_404(Route, id=route_id)
        comments = routes.comments.all().order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 작성
    def post(self, request, route_id):
        serializer = CommentCreateSerializer(data=request.data)
        
        if not request.user.is_authenticated:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(user=request.user, route_id=route_id)

        return Response(({"message": "댓글 작성 완료!"},serializer.data), status=status.HTTP_201_CREATED)
        

class CommentDetailView(APIView):
    # 로그인한 사람만 댓글 수정/삭제 가능
    permission_classes = [permissions.IsAuthenticated]
    
    # 댓글 수정
    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentCreateSerializer(comment, data=request.data)
        if comment.user == request.user:
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(({"message": "댓글 수정 완료!"}, serializer.data), status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    # 댓글 삭제
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user:
            comment.delete()
            return Response({"message": "댓글 삭제 완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class RateView(APIView):
    # 로그인한 사람만 평점을 줄 수 있음
    permission_classes = [permissions.IsAuthenticated]

    # 평점 주기
    def post(self, request, route_id):
        route = get_object_or_404(Route, id=route_id)
        rate = request.data.get('rate')

        # rate가 null값인 경우
        if not rate:
            return Response({"message": "평점을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rate = int(rate)
            if rate < 0 or rate > 100:
                return Response({"message": "평점은 0부터 100까지의 정수로 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"message": "평점은 0부터 100까지의 정수로 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # route_rate는 새로 생성했거나 사져온 RouteRate 객체
        # created는 새로 생성된 객체인지 나타내는 bool값
        route_rate, created = RouteRate.objects.get_or_create(route=route, user=request.user)
        route_rate.rate = rate
        route_rate.save()

        # created의 불린값을 이용해 문구를 다르게 만들 수 있다.
        if created:
            return Response({"message": f"{rate}점이 등록되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({f"message": f"{rate}점으로 업데이트되었습니다."}, status=status.HTTP_200_OK)