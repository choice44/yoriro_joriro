from rest_framework.test import APITestCase
from rest_framework import status

from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from django.urls import reverse

from PIL import Image
import tempfile

from users.models import User


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(temp_file, "png")
    return temp_file


class JoriroCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "aaa@aaa.com",
                         "nickname": "aaa", "password": "password"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "password")

    def setUp(self):
        self.access_token = self.client.post(
            reverse('token_obtain_pair'), self.user_data).data['access']

    # 정상적인 조리로 이용
    def test_pass_joriro_create(self):
        temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
        temp_file.name = "image.png"  # 임시 파일 이름 지정
        # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
        image_file = get_temporary_image(temp_file)
        # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
        image_file.seek(0)

        data = {}
        data["image"] = image_file
        data["model"] = 3
        data["place"] = 3

        response = self.client.post(
            path=reverse("joriro_view"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 모델 없이 테스트
    def test_pass_joriro_create_without_model(self):
        temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
        temp_file.name = "image.png"  # 임시 파일 이름 지정
        # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
        image_file = get_temporary_image(temp_file)
        # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
        image_file.seek(0)

        data = {}
        data["image"] = image_file
        data["place"] = 3

        response = self.client.post(
            path=reverse("joriro_view"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 여행지 없이 테스트
    def test_fail_joriro_create_without_place(self):
        temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
        temp_file.name = "image.png"  # 임시 파일 이름 지정
        # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
        image_file = get_temporary_image(temp_file)
        # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
        image_file.seek(0)

        data = {}
        data["image"] = image_file
        data["model"] = 3

        response = self.client.post(
            path=reverse("joriro_view"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 이미지 없이 테스트
    def test_fail_joriro_create_without_image(self):
        data = {}
        data["model"] = 3
        data["place"] = 3

        response = self.client.post(
            path=reverse("joriro_view"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 로그인 안하고 테스트
    def test_fail_joriro_create_without_login(self):
        temp_file = tempfile.NamedTemporaryFile()  # 임시 파일 생성
        temp_file.name = "image.png"  # 임시 파일 이름 지정
        # 맨 위의 함수에 넣어서 이미지 파일을 받아온다.
        image_file = get_temporary_image(temp_file)
        # 이미지의 첫번째 프레임을 받아온다. 그냥 파일이기 때문에 첫번째 프레임을 받아오는 과정 필요.
        image_file.seek(0)

        data = {}
        data["image"] = image_file
        data["model"] = 3
        data["place"] = 3

        response = self.client.post(
            path=reverse("joriro_view"),
            data=encode_multipart(data=data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
