import json, os
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework.test import APITestCase, APIClient

# 이미지
from PIL import Image
import tempfile
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY

from routes.models import Route, Comment, RouteRate, RouteArea, RouteSpot
from spots.models import Area, Sigungu, Spot
from users.models import User
from routes.views import RouteView, SpotCreateView, RouteDetailView, CommentView, CommentDetailView, RateView


def get_temporary_image():
    image = Image.new('RGB', (100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, 'JPEG')
    temp_file.seek(0)
    return temp_file

# RouteView 테스트
class RouteViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", nickname="test")
        self.user.set_password('test')
        self.user.save()
        self.user_data = {"email": "test@test.com", "password": "test"}
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data['access']
        self.area = Area.objects.create(id=1, name="서울")
        self.spot1 = Spot.objects.create(id=111, title="spot1", type=99, mapx=11.11, mapy=22.22)
        self.spot2 = Spot.objects.create(id=222, title="spot2", type=99, mapx=33.33, mapy=44.44)
        self.spot3 = Spot.objects.create(id=333, title="spot3", type=99, mapx=55.55, mapy=66.66)
        self.spot4 = Spot.objects.create(id=444, title="spot3", type=99, mapx=77.77, mapy=88.88)
        
    def tearDown(self):
        for route in Route.objects.all():
            route.image.delete()
        
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
            'spots': [{'spot':self.spot1.id, 'order':1, 'day':1},
                      {'spot':self.spot2.id, 'order':2, 'day':1},
                      {'spot':self.spot3.id, 'order':1, 'day':2},
                      {'spot':self.spot4.id, 'order':2, 'day':2}],
            'content': "content"
        }
        # 게시글 데이터를 가지고 post 요청
        response = self.client.post(
            path=reverse("route_view"),
            data=route_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().title, "route_test")
        self.assertEqual(len(response.data[1]['spots']), 4)
        
    # 여행루트 게시글 작성 테스트(이미지가 있을 때)
    def test_route_view_post_with_image(self):
        # 임시 이미지 생성
        image_file = get_temporary_image()
        # ContentFile(파일내용, 파일이름)은 파일이름과 내용을 메모리에 저장함
        # image_file변수에 ContentFile객체를 저장해 게시글 요청 시 첨부하여 서버전송이 가능해짐
        image_file = ContentFile(image_file.read(), 'example.jpg')

        # 파이썬 객체로 되어있는 것들은 json.dumps()를 이용해 json문자열로 변환해줘야한다.
        route_data = {
            'user': self.user.id,
            'title': 'route_test',
            'duration': 1,
            'cost': 1000,
            'areas': json.dumps({
                'area': self.area.id,
                'sigungu': 1
            }),
            'spots':  json.dumps([{'spot':self.spot1.id, 'order':1, 'day':1},
                      {'spot':self.spot2.id, 'order':2, 'day':1},
                      {'spot':self.spot3.id, 'order':1, 'day':2},
                      {'spot':self.spot4.id, 'order':2, 'day':2}]),
            'content': "content",
            'image': image_file
        }

        response = self.client.post(
            path=reverse("route_view"),
            data=route_data,
            format='multipart',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().title, "route_test")
        # assertTrue는 True, False로 판단
        # startswith(문자열)는 앞부분이 문자열과 같은지 확인, 이미지 뒤에 랜덤문자가 붙어서 사용함
        self.assertTrue(os.path.basename(response.data[1]['image']).startswith('example'))
        self.assertEqual(len(response.data[1]['spots']), 4)

# 스팟 생성 테스트
class SpotCreateViewTest(APITestCase):
    def setUp(self):
        self.spot1 = Spot.objects.create(id=111, title="spot1", type=99, mapx=11.11, mapy=22.22)

    def test_spot_create_view_post(self):
        self.assertEqual(Spot.objects.count(), 1)
        self.assertEqual(Spot.objects.get().title, "spot1")

# RouteDetailView 테스트
class RouteDetailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", nickname="test")
        self.user.set_password('test')
        self.user.save()
        self.user_data = {"email": "test@test.com", "password": "test"}
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data['access']
        self.area = Area.objects.create(id=1, name="서울")
        self.spot1 = Spot.objects.create(id=111, title="spot1", type=99, mapx=11.11, mapy=22.22)
        self.spot2 = Spot.objects.create(id=222, title="spot2", type=99, mapx=33.33, mapy=44.44)
        self.spot3 = Spot.objects.create(id=333, title="spot3", type=99, mapx=55.55, mapy=66.66)
        self.spot4 = Spot.objects.create(id=444, title="spot4", type=99, mapx=77.77, mapy=88.88)
        
        
        image_file = get_temporary_image()
        image_file = ContentFile(image_file.read(), 'example.jpg')

        route_data = {
            'title': 'route_test',
            'duration': 1,
            'cost': 1000,
            'content': "content",
            'image': image_file
        }

        self.route = Route.objects.create(user=self.user, **route_data)

        RouteArea.objects.create(route=self.route, area=self.area, sigungu=1)

        RouteSpot.objects.create(route=self.route, spot=self.spot1, order=1, day=1)
        RouteSpot.objects.create(route=self.route, spot=self.spot2, order=2, day=1)
        RouteSpot.objects.create(route=self.route, spot=self.spot3, order=1, day=2)
        RouteSpot.objects.create(route=self.route, spot=self.spot4, order=2, day=2)


    def tearDown(self):
        for route in Route.objects.all():
            route.image.delete()

    # 상세페이지 데이터 불러오기
    def test_route_detail_view_get(self):
        response = self.client.get(path=reverse("route_detail_view", kwargs={"route_id": self.route.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['spots']), 4)

    def test_route_detail_view_put(self):
        # 수정할 지역, 목적지 생성
        new_area = Area.objects.create(id=2, name="인천")
        new_spot1 = Spot.objects.create(id=555, title="spot5", type=99, mapx=99.99, mapy=10.10)
        new_spot2 = Spot.objects.create(id=666, title="spot6", type=99, mapx=12.12, mapy=13.13)
        
        update_image_file = get_temporary_image()
        update_image_file = ContentFile(update_image_file.read(), 'update.jpg')
        
        # 수정할 루트 데이터
        updated_route_data = {
            'title': 'updated_route_test',
            'duration': 2,
            'cost': 2000,
            'content': "updated_content",
            'image': update_image_file,
            'areas': json.dumps({'area': new_area.id, 'sigungu': 1}),
            'spots': json.dumps([{'spot': new_spot1.id, 'order': 1, 'day': 1},
                      {'spot': self.spot2.id, 'order': 2, 'day': 1},
                      {'spot': new_spot2.id, 'order': 1, 'day': 2},
                      {'spot': self.spot4.id, 'order': 2, 'day': 2}]),
        }
        response = self.client.put(
            path=reverse("route_detail_view", kwargs={"route_id": self.route.id}),
            data=updated_route_data,
            format='multipart',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        updated_route = Route.objects.get(id=self.route.id)
        
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_route.title, "updated_route_test")
        self.assertEqual(updated_route.duration, 2)
        self.assertEqual(updated_route.cost, 2000)
        self.assertEqual(updated_route.content, "updated_content")
        self.assertEqual(os.path.basename(updated_route.image.name), 'update.jpg')
        self.assertEqual(updated_route.areas.first().area.id, new_area.id)
        self.assertIn(new_spot1.id, [spot.id for spot in updated_route.spots.all()])
        self.assertIn(new_spot2.id, [spot.id for spot in updated_route.spots.all()])

    def test_route_detail_view_delete(self):
        
        pass


class CommentViewTest(APITestCase):
    pass


class CommentDetailViewTest(APITestCase):
    pass


class RateViewTest(APITestCase):
    pass
