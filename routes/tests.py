import json, os
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework.test import APITestCase
# 이미지
from PIL import Image
import tempfile

from routes.models import Route, Comment, RouteRate, RouteArea, RouteSpot
from spots.models import Area, Spot
from users.models import User

# 임시 이미지 생성
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
        
    # 로그인 시 여행루트 게시글 작성 테스트
    def test_route_view_post_login(self):
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
    
    # 비로그인 시 여행루트 게시글 작성 테스트    
    def test_route_view_post_not_login(self):
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
        )

        self.assertEqual(response.status_code, 401)
        
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

# 상세페이지 테스트
class RouteDetailViewTest(APITestCase):
    def setUp(self):
        # 유저1
        self.user1 = User.objects.create(email="test@test.com", nickname="test1")
        self.user1.set_password('test')
        self.user1.save()
        # 유저2
        self.user2 = User.objects.create(email="test@naver.com", nickname="test2")
        self.user2.set_password('test')
        self.user2.save()
        # 유저 1,2 토큰
        self.user1_data = {"email": "test@test.com", "password": "test"}
        self.user2_data = {"email": "test@naver.com", "password": "test"}
        self.access_token1 = self.client.post(reverse("token_obtain_pair"), self.user1_data).data['access']
        self.access_token2 = self.client.post(reverse("token_obtain_pair"), self.user2_data).data['access']
        
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

        self.route = Route.objects.create(user=self.user1, **route_data)

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

    # 로그인 시 여행루트 수정 테스트
    def test_route_detail_view_put_login(self):
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
            HTTP_AUTHORIZATION=f"Bearer {self.access_token1}",
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
    
    # 본인이 아닐 시 여행루트 수정    
    def test_route_detail_view_put_not_author(self):
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
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        
        self.assertEqual(response.status_code, 403)
    
    # 비로그인 시 여행루트 수정    
    def test_route_detail_view_put_not_login(self):
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
        )
        
        self.assertEqual(response.status_code, 401)

    # 로그인 시 여행루트 삭제 테스트
    def test_route_detail_view_delete_login(self):
        response = self.client.delete(
            path=reverse("route_detail_view", kwargs={"route_id": self.route.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token1}",
        )

        self.assertEqual(response.status_code, 204)
        
    # 본인이 아닐 시 여행루트 삭제
    def test_route_detail_view_delete_not_author(self):
        response = self.client.delete(
            path=reverse("route_detail_view", kwargs={"route_id": self.route.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )

        self.assertEqual(response.status_code, 403)
        
    # 비로그인 시 여행루트 삭제
    def test_route_detail_view_delete_not_login(self):
        response = self.client.delete(
            path=reverse("route_detail_view", kwargs={"route_id": self.route.id}),
        )

        self.assertEqual(response.status_code, 401)

# 여행루트 댓글 테스트
class CommentViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", nickname="test")
        self.user.set_password('test')
        self.user.save()
        self.user_data = {"email": "test@test.com", "password": "test"}
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data['access']
        self.route = Route.objects.create(user=self.user,
                                          title="route_test",
                                          duration=1,
                                          cost=0,
                                          content="content")
        self.comment_data = {"content": "test_comment"}
        
    def tearDown(self):
        for route in Route.objects.all():
            route.image.delete()

    # 댓글 불러오기
    def test_get_comments(self):
        Comment.objects.create(user=self.user, route=self.route, content="test_comment")
        response = self.client.get(reverse("comment_view", kwargs={"route_id": self.route.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['content'], "test_comment")

    # 로그인 시 댓글 등록 테스트
    def test_post_comment_login(self):
        response = self.client.post(
            path=reverse("comment_view", kwargs={"route_id": self.route.id}),
            data=self.comment_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data[1]['content'], "test_comment")

    # 비로그인 시 댓글 등록 테스트
    def test_post_comment_not_login(self):
        response = self.client.post(
            path=reverse("comment_view", kwargs={"route_id": self.route.id}),
            data=self.comment_data,
            format='json'
        )
        self.assertEqual(response.status_code, 401)


# 여행루트 댓글 수정, 삭제 테스트
class CommentDetailViewTest(APITestCase):
    def setUp(self):
        # 유저1
        self.user1 = User.objects.create(email="test@test.com", nickname="test1")
        self.user1.set_password('test')
        self.user1.save()
        # 유저2
        self.user2 = User.objects.create(email="test@naver.com", nickname="test2")
        self.user2.set_password('test')
        self.user2.save()
        # 유저 1,2 토큰
        self.user1_data = {"email": "test@test.com", "password": "test"}
        self.user2_data = {"email": "test@naver.com", "password": "test"}
        self.access_token1 = self.client.post(reverse("token_obtain_pair"), self.user1_data).data['access']
        self.access_token2 = self.client.post(reverse("token_obtain_pair"), self.user2_data).data['access']
        # 여행루트 정보
        self.route = Route.objects.create(user=self.user1,
                                          title="route_test",
                                          duration=1,
                                          cost=0,
                                          content="content")
        self.comment = Comment.objects.create(user=self.user1, route=self.route, content='content')
    
    def tearDown(self):
        for route in Route.objects.all():
            route.image.delete()
            
    # 로그인 시 댓글 수정
    def test_put_comment_login(self):
        comment_data = {'content': 'updated content'}
        response = self.client.put(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
            data=comment_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token1}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[1]['content'], 'updated content')
    
    # 본인이 아닐 시 댓글 수정
    def test_put_comment_not_author(self):
        comment_data = {'content': 'updated content'}
        response = self.client.put(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
            data=comment_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )

        self.assertEqual(response.status_code, 403)
    
    # 비로그인 시 댓글 수정    
    def test_put_comment_not_login(self):
        comment_data = {'content': 'updated content'}
        response = self.client.put(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
            data=comment_data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)
    
    # 로그인 시 댓글 삭제
    def test_delete_comment_login(self):
        response = self.client.delete(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token1}"
        )

        self.assertEqual(response.status_code, 204)
    
    # 본인이 아닐 시 댓글 삭제    
    def test_delete_comment_not_author(self):
        response = self.client.delete(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}"
        )

        self.assertEqual(response.status_code, 403)
    
    # 비로그인 시 댓글 삭제     
    def test_delete_comment_not_login(self):
        response = self.client.delete(
            path=reverse("comment_detail_view", kwargs={'comment_id': self.comment.id}),
        )

        self.assertEqual(response.status_code, 401)

# 여행루트 평점 테스트
class RateViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", nickname="test")
        self.user.set_password('test')
        self.user.save()
        self.user_data = {"email": "test@test.com", "password": "test"}
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data['access']
        self.route = Route.objects.create(user=self.user,
                                          title="route_test",
                                          duration=1,
                                          cost=0,
                                          content="content")

    def tearDown(self):
        for route in Route.objects.all():
            route.image.delete()
    
    # 여행루트 평점 등록
    def test_create_rate_login(self):
        rate_data = {'rate': 50}
        response = self.client.post(
            path=reverse("rate_view", kwargs={'route_id': self.route.id}),
            data=rate_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '50점이 등록되었습니다.')
        
    # 비로그인 시 평점 등록    
    def test_create_rate_not_login(self):
        rate_data = {'rate': 50}
        response = self.client.post(
            path=reverse("rate_view", kwargs={'route_id': self.route.id}),
            data=rate_data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    # 여행루트 평점 재등록
    def test_update_rate(self):
        rate = RouteRate.objects.create(user=self.user, route=self.route, rate=70)
        
        rate_data = {'rate': 80}
        response = self.client.post(
            path=reverse("rate_view", kwargs={'route_id': self.route.id}),
            data=rate_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '80점으로 업데이트되었습니다.')

    # 여행루트 입력 값 이상의 숫자 등록
    def test_invalid_rate(self):
        rate_data = {'rate': 101}
        response = self.client.post(
            path=reverse("rate_view", kwargs={'route_id': self.route.id}),
            data=rate_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 400)