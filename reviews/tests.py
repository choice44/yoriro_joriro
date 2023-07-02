from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile, random
from faker import Faker
from datetime import datetime

from users.models import User
from reviews.models import Review
from spots.models import Spot, Area
from reviews.serializers import ReviewDetailSerializer, ReviewListSerializer, ReviewCreateSerializer, ReviewUpdateSerializer


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


# view = ReviewView, url name = "review_view", method = post
class ReviewCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):

        cls.faker = Faker()
        
        cls.author_data_list = []
        cls.authors = []
        for i in range(10):
            cls.author_data = {
                "email": f"{cls.faker.unique.email()}",
                "password": f"{cls.faker.word()}"
            }
            cls.author_data_list.append(cls.author_data)
            cls.author = User.objects.create(**cls.author_data, nickname=cls.faker.unique.name())
            cls.author.set_password(cls.author_data["password"])
            cls.author.save()
            cls.authors.append(cls.author) 
        
        cls.spots=[]
        for i in range(10):
            cls.spots.append(Spot.objects.create(
                type=random.choice([12, 39]),
                title=cls.faker.word(), 
                mapx=cls.faker.longitude(), 
                mapy=cls.faker.latitude()
                ))

        cls.review_data_list=[]
        for i in range(10):
            cls.review_data = {
                "title": f"{cls.faker.word()}",
                "content": f"{cls.faker.sentence()}",
                "visited_date": f"{cls.faker.date()}",
                "rate": random.randint(1, 5),
                "spot": cls.spots[random.randint(0, 9)].id   
            }
            cls.review_data_list.append(cls.review_data)
    

    def setUp(self):
        
        self.author_tokens = []
        
        for i in range(10):
            self.author_tokens.append(self.client.post(reverse("token_obtain_pair"), self.author_data_list[i]).data["access"])

        
    # 테스트 후 이미지 파일 삭제하기
    def tearDown(self):
        for review in Review.objects.all():
            review.image.delete()
            review.delete()


    # 게시글 작성 성공(NOT NULL(title, content, spot, rate, visited_date))
    def test_pass_create_review(self):
        for i in range(10):

            response = self.client.post(
                path=reverse("review_view"),
                data=self.review_data_list[i],
                HTTP_AUTHORIZATION=f"Bearer {self.author_tokens[i]}",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data[0]["message"], "관광지 리뷰 작성 완료!")
            self.assertEqual(Review.objects.count(), i+1)
            self.assertEqual(Review.objects.get(id=i+1).title, self.review_data_list[i]["title"])
            self.assertEqual(Review.objects.get(id=i+1).content, self.review_data_list[i]["content"])
            self.assertEqual(Review.objects.get(id=i+1).spot_id, self.review_data_list[i]["spot"])
            self.assertEqual(str(Review.objects.get(id=i+1).visited_date), self.review_data_list[i]["visited_date"])
            self.assertEqual(Review.objects.get(id=i+1).rate, self.review_data_list[i]["rate"])


    # 이미지가 있는 리뷰 작성 성공
    def test_pass_create_review_with_image(self):
            
        for i in range(10):
            
            temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
            temp_file.name = f"image{i}.png"  # 임시 파일 이름 지정
            image_file = get_temporary_image(temp_file)  # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
            image_file.seek(0)  # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
            
            self.review_data_list[i]["image"] = image_file

            response = self.client.post(
                path=reverse("review_view"),
                data=encode_multipart(data=self.review_data_list[i], boundary=BOUNDARY),
                content_type=MULTIPART_CONTENT,
                HTTP_AUTHORIZATION=f"Bearer {self.author_tokens[i]}",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Review.objects.count(), i+1)
            self.assertEqual(Review.objects.get(id=i+1).title, self.review_data_list[i]["title"])
            self.assertEqual(Review.objects.get(id=i+1).content, self.review_data_list[i]["content"])
            self.assertEqual(Review.objects.get(id=i+1).spot_id, self.review_data_list[i]["spot"])
            self.assertEqual(str(Review.objects.get(id=i+1).visited_date), self.review_data_list[i]["visited_date"])
            self.assertEqual(Review.objects.get(id=i+1).rate, self.review_data_list[i]["rate"])
            self.assertEqual(str(Review.objects.get(id=i+1).image), f"review/images/{datetime.now().strftime('%Y/%m/')+temp_file.name}")
      
      
    # 로그인 안 했을 때 리뷰 작성 실패
    def test_fail_create_review_if_not_logged_in(self):
        for i in range(10):
            url = reverse("review_view")
            response = self.client.post(url, self.review_data_list[i])
            self.assertEqual(response.status_code, 401)


class ReviewReadTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.reviews=[]
        cls.areas=[]
        area_ids=[1, 2, 3, 4, 5, 6, 7, 8, 31, 32, 33, 34, 35, 36, 37, 38, 39]
        
        for i in range(17):
            cls.areas.append(Area.objects.create(
                name=cls.faker.city(),
                id=area_ids[i]
                ))
            
        for i in range(10):
            cls.user = User.objects.create(
                email=cls.faker.unique.email(), 
                password=cls.faker.word(), 
                nickname=cls.faker.unique.name()
                )

            cls.spot = Spot.objects.create(
                type=random.choice([12, 39]),
                area=cls.areas[random.randint(0, 16)],
                sigungu=random.randint(1,25),
                addr1=cls.faker.address(),
                title=cls.faker.word(), 
                mapx=cls.faker.longitude(), 
                mapy=cls.faker.latitude()
                )
            
            cls.reviews.append(Review.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                spot=cls.spot,
                visited_date=cls.faker.date(),
                rate=random.randint(1,5)
                ))


    # # 리뷰 전체 목록 조회 성공
    # # view = ReviewView, url name = "review_view", method = get
    # def test_pass_review_list(self):
    #     response = self.client.get(path=reverse("review_view"))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 10)


    # 리뷰 전체 목록 페이지네이션(page_size=6)조회 성공
    # view = ReviewFilterView, url name = "review_filter_view", method = get
    def test_pass_review_paginated_list(self):
        response = self.client.get(path=reverse("review_filter_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)
        
    
    # 리뷰 관광지 목록 페이지네이션(page_size=6)조회 성공
    # view = ReviewFilterView, url name = "review_filter_view", method = get
    def test_pass_review_filtered_12_list(self):
        response = self.client.get("/reviews/filter/", {"spot__type": "12"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 12)
        
        
    # 리뷰 맛집 목록 페이지네이션(page_size=6)조회 성공
    # view = ReviewFilterView, url name = "review_filter_view", method = get
    def test_pass_review_filtered_39_list(self):
        response = self.client.get("/reviews/filter/", {"spot__type": "39"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 39)


    # 리뷰 상세 보기(10개 테스트) 성공
    # view = ReviewDetailView, url name = "review_detail_view", method = get
    def test_pass_review_detail(self):
        for review in self.reviews:
            url = review.get_absolute_url()
            response = self.client.get(url)
            serializer = ReviewDetailSerializer(review).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)


# view = ReviewDetailView, url name = "review_detail_view", method = delete
class ReviewDeleteTest(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1@test.com", "password": "password"}
        cls.user = User.objects.create_user("test1@test.com", "test1_nickname", "password")
        
        cls.another_user_data = {"email": "else1@test.com", "password": "password"}
        cls.another_user = User.objects.create(email="else1@test.com", password="password", nickname="someone")
        cls.another_user.set_password("password")
        cls.another_user.save()
        
        cls.faker = Faker()
        cls.areas=[]
        area_ids=[1, 2, 3, 4, 5, 6, 7, 8, 31, 32, 33, 34, 35, 36, 37, 38, 39]
        
        for i in range(17):
            cls.areas.append(Area.objects.create(
                name=cls.faker.city(),
                id=area_ids[i]
                ))
            
        cls.spots=[]
        for i in range(10):
            cls.spots.append(Spot.objects.create(
                type=random.choice([12, 39]),
                area=cls.areas[random.randint(0, 16)],
                sigungu=random.randint(1,25),
                addr1=cls.faker.address(),
                title=cls.faker.word(), 
                mapx=cls.faker.longitude(), 
                mapy=cls.faker.latitude()
                ))
            
        cls.reviews=[]
        for i in range(10):
            cls.reviews.append(Review.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                spot=cls.spots[random.randint(0, 9)],
                visited_date=cls.faker.date(),
                rate=random.randint(1,5)
                ))
        
        Review.objects.filter(id=5).delete()

    def setUp(self):
        self.user_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.another_user_token = self.client.post(reverse("token_obtain_pair"), self.another_user_data).data["access"]


    # 리뷰 삭제 성공(204_NO_CONTENT)
    def test_pass_delete_review(self):
        response = self.client.delete(
            path = reverse("review_detail_view", kwargs={"review_id": 1}),
            HTTP_AUTHORIZATION = f"Bearer {self.user_token}"
        )
        self.assertEqual(response.status_code, 204)
        
        
    # 로그인 안하고 리뷰 삭제 실패(401_UNAUTHORIZED)
    def test_fail_delete_review_if_not_logged_in(self):
        url = reverse("review_detail_view", kwargs={"review_id": 2})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)


    # 다른 사람의 리뷰 삭제 실패(403_FORBIDDEN)
    def test_fail_delete_review_if_not_author(self):
        response = self.client.delete(
            path = reverse("review_detail_view", kwargs={"review_id": 3}),
            HTTP_AUTHORIZATION = f"Bearer {self.another_user_token}"
        )
        self.assertEqual(response.status_code, 403)


    # 없는 리뷰 삭제 실패(404_NOT_FOUND)
    def test_fail_delete_review_if_not_exist(self):
        response = self.client.delete(
            path = reverse("review_detail_view", kwargs={"review_id": 5}),
            HTTP_AUTHORIZATION = f"Bearer {self.user_token}"
        )
        self.assertEqual(response.status_code, 404)
                        