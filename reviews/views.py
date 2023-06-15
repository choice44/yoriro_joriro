from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from reviews.models import Review
from reviews.serializers import (
    ReviewListSerializer,
    ReviewDetailSerializer,
    ReviewUpdateSerializer,
    ReviewCreateSerializer
)


# reviews/filter/
class ReviewFilterView(ListAPIView):
    """
    타입/지역별 리뷰 목록 조회
    """
    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields  = ["spot__type", "spot__area", "spot__sigungu"]


# reviews/
class ReviewView(APIView):
    # 로그인한 사람은 리뷰 작성 가능. 아니면 리뷰 전체 목록 조회만 가능.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    """
    리뷰 전체 목록 조회
    """

    def get(self, request):
        reviews = Review.objects.all().order_by("-created_at")
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """
    리뷰 작성
    """

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(({"message": "관광지 리뷰 작성 완료!"}, serializer.data), status=status.HTTP_201_CREATED)


# reviews/<int:review_id>/
class ReviewDetailView(APIView):
    # 로그인한 사람은 리뷰 수정/삭제 가능. 아니면 리뷰 상세보기만 가능.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    """
    리뷰 상세보기
    """

    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewDetailSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """
    리뷰 수정하기
    """

    def put(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        if review.user == request.user:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(({"message": "관광지 리뷰 수정 완료!"},serializer.data), status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    """
    리뷰 삭제하기
    """

    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        if review.user == request.user:
            review.delete()
            return Response({"message": "관광지 리뷰 삭제 완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


# reviews/<int:review_id>/like/
class ReviewLikeView(APIView):
    """
    리뷰 좋아요
    """
    
    # 로그인한 사람만 좋아요 가능
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id = review_id)
        if request.user in review.likes.all():
            review.likes.remove(request.user)
            return Response({"message":"좋아요를 취소했습니다."}, status=status.HTTP_200_OK)
        else:
            review.likes.add(request.user)
            return Response({"message":"좋아요를 눌렀습니다."}, status=status.HTTP_200_OK)
