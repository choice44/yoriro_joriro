import json
from rest_framework.test import APITestCase, APIClient

# 이미지
from PIL import Image
import tempfile
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY

from routes.models import Route, Comment, RouteRate, RouteArea
from spots.models import Area, Sigungu, Spot
from users.models import User
from routes.views import RouteView, SpotCreateView, RouteDetailView, CommentView, CommentDetailView, RateView


def get_temporary_image():
    image = Image.new('RGB', (100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, 'JPEG')
    temp_file.seek(0)
    return temp_file

class RouteViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            nickname='test',
            password='0000'
        )
        
        # Route안에 있는 애들이 아니라서 별도로 객체를 생성 시켜줌
        self.area = Area.objects.create(name='서울')
        self.spot1 = Spot.objects.create(title='남산타워', area=self.area, type=12, mapx=1.0, mapy=1.0)
        self.spot2 = Spot.objects.create(title='롯데타워', area=self.area, type=39, mapx=2.0, mapy=2.0)

        
        # CharField나 TextField는 null=True 옵션이 없어도 명시적으로 ""가 들어감
        # 반면 IntegerField의 경우 null=True 옵션이 없으면 NOT NULL조건이 적용됨
        self.route = Route.objects.create(user=self.user,
                                          title='route_test',
                                          duration=1,
                                          cost=1000,
                                          content="content"
                                          )
        # RouteArea 객체 생성
        self.routearea = RouteArea.objects.create(route=self.route, area=self.area, sigungu=1)
        # route의 areas 항목에 추가
        self.route.areas.set([self.routearea])

        # 루트에 목적지 추가
        self.route.spots.set([self.spot1, self.spot2])
        
        self.client = APIClient()
        
        ## 로그인
        self.client.force_authenticate(user=self.user)

    def test_route_view_get(self):
        response = self.client.get(f'/routes/{self.route.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'route_test')
        self.assertEqual(len(response.data['spots']), 2)

    # 여행루트 게시글 작성 테스트
    def test_route_view_post(self):
        route_data = {
            'user': self.user.id,
            'title': 'route_test',
            'duration': 1,
            'cost': 1000,
            'areas': {
                'area': self.area.id,
                'sigungu': 1
            },
            'spots': [self.spot1.id, self.spot2.id],
            'content': "content"
        }
        # 게시글 데이터를 가지고 post 요청
        response = self.client.post('/routes/', data=route_data, format='json')

        self.assertEqual(response.status_code, 201) # 서버 응답확인
        self.assertEqual(response.data[1]['title'], 'route_test')   # 데이터 일치 여부
        self.assertEqual(len(response.data[1]['spots']), 2) # spots의 갯수가 맞는지
        self.assertEqual(len(response.data[1]['areas']), 1) # areas의 갯수가 맞는지
        
    # 여행루트 게시글 작성 테스트(이미지가 있을 때)
    def test_route_view_post_with_image(self):
        # 임시 이미지 생성
        image_file = get_temporary_image()
        route_data = {
            'user': self.user.id,
            'title': 'route_test',
            'duration': 1,
            'cost': 1000,
            'areas': json.dumps({   # 파이썬 객체를 JSon으로 변환
            'area': self.area.id,
            'sigungu': 1
            }),
            'spots': [self.spot1.id,  self.spot2.id],
            'content': "content",
            'image': image_file
        }
        # encode_multipart: 파일과 일반 post데이터를 포함하는 인코딩 데이터를 생성
        response = self.client.post('/routes/', encode_multipart(data=route_data, boundary=BOUNDARY), content_type=MULTIPART_CONTENT)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data[1]['title'], 'route_test')
        self.assertEqual(len(response.data[1]['spots']), 2)
        self.assertEqual(len(response.data[1]['areas']), 1)

class SpotCreateViewTest(APITestCase):
    def setUp(self):

        pass

    def test_spot_create_view_post(self):
        
        pass


class RouteDetailViewTest(APITestCase):
    def setUp(self):

        pass

    def test_route_detail_view_get(self):
        
        pass

    def test_route_detail_view_put(self):
        
        pass

    def test_route_detail_view_delete(self):
        
        pass


class CommentViewTest(APITestCase):
    pass


class CommentDetailViewTest(APITestCase):
    pass


class RateViewTest(APITestCase):
    pass
