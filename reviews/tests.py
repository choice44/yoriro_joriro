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


    # 리뷰 작성 성공(NOT NULL(title, content, spot, rate, visited_date))
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
            
        cls.viewers_data = []
        cls.viewers = []
        for i in range(10):
            cls.viewer_data = {
                "email": f"{cls.faker.unique.email()}",
                "password": f"{cls.faker.word()}"
            }
            cls.viewers_data.append(cls.viewer_data)
            cls.viewer = User.objects.create(**cls.viewer_data, nickname=cls.faker.unique.name())
            cls.viewer.set_password(cls.viewer_data["password"])
            cls.viewer.save()
            cls.viewers.append(cls.viewer)
        
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
            
            cls.like_viewers=[]
            for j in range(i+1):
                cls.like_viewers.append(cls.viewers[j])
                
            cls.reviews[i].likes.set(cls.like_viewers)
     
        cls.search_spot = Spot.objects.create(
            type=random.choice([12, 39]),
            area=cls.areas[random.randint(0, 16)],
            sigungu=random.randint(1,25),
            addr1=cls.faker.address(),
            title=cls.faker.word(), 
            mapx=cls.faker.longitude(), 
            mapy=cls.faker.latitude()
            )
        
        cls.spot_reviews=[]
        for i in range(10):
            cls.spot_reviews.append(Review.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                spot=cls.search_spot,
                visited_date=cls.faker.date(),
                rate=random.randint(1,5)
                ))


    # 리뷰 전체 목록 페이지네이션(page_size=6)조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_list(self):
        response = self.client.get(path=reverse("review_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)


    # 특정 장소 리뷰 목록 조회 성공
    # view = ReviewFilterView, url name = "review_filter_view", method = get
    def test_pass_spot_review_list(self):
        response = self.client.get("/reviews/filter/", {"search": 11})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)
        self.assertEqual(response.data["count"], 10)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["id"], 11)
        
    
    # 리뷰 관광지 목록 조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_filtered_12_list(self):
        response = self.client.get("/reviews/", {"type": "12"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 12)
        
        
    # 리뷰 맛집 목록 조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_filtered_39_list(self):
        response = self.client.get("/reviews/", {"type": "39"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 39)
            
            
    # 리뷰 좋아요순 목록 조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_ordered_by_like_count_list(self):
        response = self.client.get("/reviews/", {"order": "like_count"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["like_count"], 10-i)
            

    # 리뷰 관광지 좋아요순 목록 조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_like_count_12_list(self):
        response = self.client.get("/reviews/", {"order": "like_count", "type": "12"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        previous = 10
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 12)
            self.assertTrue(previous>=response.data["results"][i]["like_count"])
            previous = response.data["results"][i]["like_count"]
            
            
    # 리뷰 맛집 좋아요순 목록 조회 성공
    # view = ReviewView, url name = "review_view", method = get
    def test_pass_review_like_count_39_list(self):
        response = self.client.get("/reviews/", {"order": "like_count", "type": "39"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        previous = 10
        for i in range(len(response.data["results"])):
            self.assertEqual(response.data["results"][i]["spot"]["type"], 39)
            self.assertTrue(previous>=response.data["results"][i]["like_count"])
            previous = response.data["results"][i]["like_count"]
            

    # 리뷰 상세 보기(10개 테스트) 성공
    # view = ReviewDetailView, url name = "review_detail_view", method = get
    def test_pass_review_detail(self):
        for review in self.reviews:
            url = review.get_absolute_url()
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        

    def setUp(self):
        self.user_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.another_user_token = self.client.post(reverse("token_obtain_pair"), self.another_user_data).data["access"]


    # 리뷰 삭제 성공(204_NO_CONTENT)
    def test_pass_delete_review(self):
        for i in range(10):
            response = self.client.delete(
                path = reverse("review_detail_view", kwargs={"review_id": i+1}),
                HTTP_AUTHORIZATION = f"Bearer {self.user_token}"
            )
            self.assertEqual(response.status_code, 204)
        
        
    # 로그인 안하고 리뷰 삭제 실패(401_UNAUTHORIZED)
    def test_fail_delete_review_if_not_logged_in(self):
        for i in range(10):
            url = reverse("review_detail_view", kwargs={"review_id": i+1})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, 401)


    # 다른 사람의 리뷰 삭제 실패(403_FORBIDDEN)
    def test_fail_delete_review_if_not_author(self):
        for i in range(10):
            response = self.client.delete(
                path = reverse("review_detail_view", kwargs={"review_id": i+1}),
                HTTP_AUTHORIZATION = f"Bearer {self.another_user_token}"
            )
            self.assertEqual(response.status_code, 403)


    # 없는 리뷰 삭제 실패(404_NOT_FOUND)
    def test_fail_delete_review_if_not_exist(self):
        for i in range(10):
            
            Review.objects.filter(id=i+1).delete()
            
            response = self.client.delete(
                path = reverse("review_detail_view", kwargs={"review_id": i+1}),
                HTTP_AUTHORIZATION = f"Bearer {self.user_token}"
            )
            self.assertEqual(response.status_code, 404)


# view = LikeView, url name = "review_like_view", method = post
class LikeTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user_data = {"email": "test@test.com", "password": "Test1234!"}
        cls.area = Area.objects.create(
                name=cls.faker.city(),
                id=random.choice([1, 2, 3, 4, 5, 6, 7, 8, 31, 32, 33, 34, 35, 36, 37, 38, 39])
                )
        cls.spot = Spot.objects.create(
                type=random.choice([12, 39]),
                area=cls.area,
                title=cls.faker.word(), 
                mapx=cls.faker.longitude(), 
                mapy=cls.faker.latitude()
                )
        cls.review_data = {"title": "test Title", "content": "test content", "rate": random.randint(1,5), "spot": cls.spot, "visited_date": cls.faker.date()}
        cls.user = User.objects.create_user("test@test.com", "test_nickname", "Test1234!")
        cls.review = Review.objects.create(**cls.review_data, user=cls.user)
        
        cls.viewers_data = []
        cls.viewers = []
        for i in range(10):
            cls.viewer_data = {
                "email": f"{cls.faker.unique.email()}",
                "password": f"{cls.faker.word()}"
            }
            cls.viewers_data.append(cls.viewer_data)
            cls.viewer = User.objects.create(**cls.viewer_data, nickname=cls.faker.unique.name())
            cls.viewer.set_password(cls.viewer_data["password"])
            cls.viewer.save()
            cls.viewers.append(cls.viewer)                    


    def setUp(self):
        self.user_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]
        self.viewer_tokens = []
        for i in range(10):
            self.viewer_tokens.append(self.client.post(
            reverse("token_obtain_pair"), self.viewers_data[i]
            ).data["access"])

    # 좋아요 성공
    def test_pass_like_review(self):
        
        # 좋아요
        for i in range(10):
            response = self.client.post(
                path=reverse("review_like_view", kwargs={"review_id": 1}),
                HTTP_AUTHORIZATION=f"Bearer {self.viewer_tokens[i]}",
            )
            serializer = ReviewDetailSerializer(self.review).data
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {'message': "좋아요를 눌렀습니다."})
            self.assertEqual(serializer["like_count"], i+1)
        
        # 좋아요 취소
        for i in range(10):
            response = self.client.post(
                path=reverse("review_like_view", kwargs={"review_id": 1}),
                HTTP_AUTHORIZATION=f"Bearer {self.viewer_tokens[i]}",
            )
            serializer = ReviewDetailSerializer(self.review).data
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {'message': "좋아요를 취소했습니다."})
            self.assertEqual(serializer["like_count"], 9-i)
    
    
    # 로그인 하지 않고 리뷰 좋아요 실패(401_UNAUTHORIZED)
    def test_fail_like_review_if_not_logged_in(self):
        for i in range(10):
            url = reverse("review_like_view", kwargs={"review_id": 1})
            response = self.client.post(url)
            self.assertEqual(response.status_code, 401)


    # 없는 리뷰 좋아요 실패(404_NOT_FOUND)
    def test_fail_like_review_if_not_exist(self):
        Review.objects.filter(id=1).delete()
        
        for i in range(10):    
            response = self.client.post(
                path = reverse("review_like_view", kwargs={"review_id": 1}),
                HTTP_AUTHORIZATION = f"Bearer {self.user_token}"
            )
            self.assertEqual(response.status_code, 404)


# view = ReviewDetailView, url name = "review_detail_view", method = put
class ReviewUpdateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test@test.com", "password": "Test1234!"}
        cls.user = User.objects.create(email="test@test.com", password="Test1234!", nickname="test")
        cls.user.set_password(cls.user_data["password"])
        cls.user.save()
        
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
        
        cls.new_reviews_data=[]
        for i in range(10):
            cls.new_reviews_data.append({
                "title": cls.faker.sentence(), 
                "content": cls.faker.text(),
                "visited_date": cls.faker.date(),
                "rate": random.randint(1,5)
                })


    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.another_user_token = self.client.post(reverse("token_obtain_pair"), self.another_user_data).data["access"]    

    
    # 테스트 후 이미지 파일 삭제하기
    def tearDown(self):
        for review in Review.objects.all():
            review.image.delete()
            review.delete()
            
    
    # 리뷰 수정 성공(NOT NULL(title, content))
    def test_pass_update_review(self):
        for i in range(10):
            url = self.reviews[i].get_absolute_url()
            response = self.client.put(
                path=url, 
                data=self.new_reviews_data[i],
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
                )
            
            # 리뷰 수정 성공(200_OK)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            updated_review = Review.objects.create(
                user=self.user, 
                title=self.new_reviews_data[i]["title"], 
                content=self.new_reviews_data[i]["content"],
                visited_date=self.new_reviews_data[i]["visited_date"],
                rate=self.new_reviews_data[i]["rate"],
                spot_id=self.reviews[i].spot.id
                )
            
            serializer = ReviewDetailSerializer(updated_review).data
            
            # 리뷰 내용 수정 됐는지
            self.assertEqual(response.data[1]["title"], serializer["title"])
            self.assertEqual(response.data[1]["content"], serializer["content"])
            self.assertEqual(response.data[1]["visited_date"], serializer["visited_date"])
            self.assertEqual(response.data[1]["rate"], serializer["rate"])
            
    
    # 이미지가 없던 리뷰에 이미지 추가해서 수정 성공
    def test_pass_update_review_add_image(self):
        for i in range(10):
            temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
            temp_file.name = f"image{i}.png"  # 임시 파일 이름 지정
            image_file = get_temporary_image(temp_file)  # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
            image_file.seek(0)  # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
            
            self.new_reviews_data[i]["image"] = temp_file
            
            url = self.reviews[i].get_absolute_url()
            response = self.client.put(
                path=url, 
                data=encode_multipart(data=self.new_reviews_data[i], boundary=BOUNDARY),
                content_type=MULTIPART_CONTENT,
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
                )
            
            # 이미지 추가하기 리뷰 수정 성공(200_OK)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            updated_review = Review.objects.create(
                user=self.user, 
                title=self.new_reviews_data[i]["title"], 
                content=self.new_reviews_data[i]["content"],
                visited_date=self.new_reviews_data[i]["visited_date"],
                rate=self.new_reviews_data[i]["rate"],
                spot_id=self.reviews[i].spot.id,
                image=f"review/images/{datetime.now().strftime('%Y/%m/')+temp_file.name}"
                )
            
            
            serializer = ReviewDetailSerializer(updated_review).data
            
            # 이미지 추가하기 리뷰 내용 수정 됐는지
            self.assertEqual(response.data[1]["title"], serializer["title"])
            self.assertEqual(response.data[1]["content"], serializer["content"])
            self.assertEqual(response.data[1]["visited_date"], serializer["visited_date"])
            self.assertEqual(response.data[1]["rate"], serializer["rate"])
            self.assertEqual(str(response.data[1]["image"]), serializer["image"])


    # 이미지 있는 리뷰 이미지 수정 성공
    def test_pass_update_review_with_another_image(self):
        for i in range(10):
            temp_file = tempfile.NamedTemporaryFile()
            temp_file.name = f"image{i}.png"
            image_file = get_temporary_image(temp_file)
            image_file.seek(0)
            
            old_review = Review.objects.get(id=i+1)
            old_review.image = f"review/images/{datetime.now().strftime('%Y/%m/')+temp_file.name}"
            old_review.save()

        for i in range(10):
            temp_file = tempfile.NamedTemporaryFile()
            temp_file.name = f"image{i+10}.png"
            image_file = get_temporary_image(temp_file)
            image_file.seek(0)
            
            self.new_reviews_data[i]["image"] = temp_file
            
            url = self.reviews[i].get_absolute_url()
            response = self.client.put(
                path=url, 
                data=encode_multipart(data=self.new_reviews_data[i], boundary=BOUNDARY),
                content_type=MULTIPART_CONTENT,
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
                )
            
            # 이미지 교체하기 리뷰 수정 성공(200_OK)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            updated_review = Review.objects.create(
                user=self.user, 
                title=self.new_reviews_data[i]["title"], 
                content=self.new_reviews_data[i]["content"],
                visited_date=self.new_reviews_data[i]["visited_date"],
                rate=self.new_reviews_data[i]["rate"],
                spot_id=self.reviews[i].spot.id,
                image=f"review/images/{datetime.now().strftime('%Y/%m/')+temp_file.name}"
                )
            
            serializer = ReviewDetailSerializer(updated_review).data
            
            # 이미지 교체하기 리뷰 내용 수정 됐는지
            self.assertEqual(response.data[1]["title"], serializer["title"])
            self.assertEqual(response.data[1]["content"], serializer["content"])
            self.assertEqual(response.data[1]["visited_date"], serializer["visited_date"])
            self.assertEqual(response.data[1]["rate"], serializer["rate"])
            self.assertEqual(str(response.data[1]["image"]), serializer["image"])

    
    # 로그인 안하고 리뷰 수정 실패(401_UNAUTHORIZED)
    def test_fail_update_review_if_not_logged_in(self):
        for i in range(10):
            url = reverse("review_detail_view", kwargs={"review_id": i+1})
            response = self.client.put(url, data=self.new_reviews_data[i])
            self.assertEqual(response.status_code, 401)
    
    
    # 다른 사람의 리뷰 수정 실패(403_FORBIDDEN)
    def test_fail_update_review_if_not_author(self):
        for i in range(10):
            response = self.client.put(
                path = reverse("review_detail_view", kwargs={"review_id": i+1}),
                data=self.new_reviews_data[i],
                HTTP_AUTHORIZATION = f"Bearer {self.another_user_token}"
            )
            self.assertEqual(response.status_code, 403)
            