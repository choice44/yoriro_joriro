from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile

from faker import Faker

from users.models import User
from .serializers import RecruitmentDetailSerializer
from .models import Recruitments, Applicant


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, 'png')
    return temp_file


class RecruitmentCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")
        cls.recruitment_data = {"title":"title", "place":"place", "content":"content", "departure":"2023-06-30", "arrival":"2023-07-02", "cost":"10000", "participant_max":"4"}

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']

    # 로그인하지 않으면 동료모집 생성 불가
    def test_fail_if_not_logged_in(self):
        url = reverse("recruitment_view")
        response = self.client.post(url, self.recruitment_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Recruitments.objects.count(), 0)

    # 로그인하면 동료모집 생성 가능
    def test_pass_create_recruitment(self):
        response = self.client.post(
            path=reverse("recruitment_view"),
            data=self.recruitment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 사진이 있는 동료모집 생성 가능
    def test_create_article_with_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.recruitment_data["image"] = image_file

        response = self.client.post(
            path=reverse("recruitment_view"),
            data=encode_multipart(data=self.recruitment_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RecruitmentReadTest(APITestCase):
    # 더미데이터 생성
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.recruitment = []
        for i in range(10):
            cls.user = User.objects.create(
                email=cls.faker.unique.email(), 
                password=cls.faker.word(), 
                nickname=cls.faker.unique.name()
                )
            cls.recruitment.append(Recruitments.objects.create(
                title=cls.faker.word(),
                place=cls.faker.word(),
                content=cls.faker.text(),
                departure=cls.faker.date()+"T00:00:00",
                arrival=cls.faker.date()+"T00:00:00",
                cost=cls.faker.random_int(),
                participant_max=int(cls.faker.random_int(2, 8)),
                user=cls.user,
                ))
    
    # 리스트 불러오기
    def test_recruitment_list(self):
        response = self.client.get(path=reverse("recruitment_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recruitments.objects.count(), 10)
        
    # 리스트 상세 페이지 확인
    def test_recruitment_detail(self):
        for recruitment in self.recruitment:
            url = recruitment.get_absolute_url()
            response = self.client.get(url)
            serializer = RecruitmentDetailSerializer(recruitment).data
            for key in serializer:
                if key not in ['is_complete', 'updated_at']:
                    if key == 'participant':
                        self.assertEqual(list(response.data[key]), list(serializer[key]))
                    else:
                        self.assertEqual(response.data[key], serializer[key])


class RecruitmentEditTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 동료모집 생성
        cls.faker = Faker()
        cls.recruitment = []
        cls.recruitment.append(Recruitments.objects.create(
            title=cls.faker.word(),
            place=cls.faker.word(),
            content=cls.faker.text(),
            departure=cls.faker.date()+"T00:00:00",
            arrival=cls.faker.date()+"T00:00:00",
            cost=cls.faker.random_int(),
            participant_max=int(cls.faker.random_int(2, 8)),
            user=cls.user,
            ))       

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]

    # 동료모집 수정 성공
    def test_recruitment_edit_seccess(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.put(
            path=url,
            data={
                "title":"edit title",
                "place":"edit place",
                "content":"edit content",
                "cost":5000,
                "participant_max":int(self.faker.random_int(2, 8)),
                "departure":self.faker.date()+"T00:00:00",
                "arrival":self.faker.date()+"T00:00:00",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Recruitments.objects.get().title, "edit title")
        

    # 동료모집 수정 성공 이미지
    def test_recruitment_edit_succenss_with_image(self):
        recruitment_data = {}
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        recruitment_data["image"] = image_file

        response = self.client.put(
            path=reverse("recruitment_detail_view", kwargs={"recruitment_id": 1}),
            data=encode_multipart(data=recruitment_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 동료모집 비로그인 수정 실패
    def test_recruitment_edit_fail_not_loggedin(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.put(
            path=url,
            data={
                "title":"edit title",
                "place":"edit place",
                "content":"edit content",
                "cost":5000,
                "participant_max":int(self.faker.random_int(2, 8)),
                "departure":self.faker.date()+"T00:00:00",
                "arrival":self.faker.date()+"T00:00:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotEqual(Recruitments.objects.get().title, "edit title")

    # 동료모집 다른유저 수정 실패
    def test_recruitment_edit_fail_not_author(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.put(
            path=url,
            data={
                "title":"edit title",
                "place":"edit place",
                "content":"edit content",
                "cost":5000,
                "participant_max":int(self.faker.random_int(2, 8)),
                "departure":self.faker.date()+"T00:00:00",
                "arrival":self.faker.date()+"T00:00:00",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(Recruitments.objects.get().title, "edit title")


class RecruitmentDeleteTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 동료모집 생성
        cls.recruitment = []
        cls.recruitment.append(Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=4,
            user=cls.user,
            ))       

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]

    # 본인 동료모집 삭제 완료
    def test_recruitment_delete_success(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 204)

    # 비로그인 동료모집 삭제 실패
    def test_recruitment_delete_fail_not_loggedin(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Recruitments.objects.get().title, "title")

    # 다른유저 동료모집 삭제 실패
    def test_recruitment_delete_fail_not_author(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 1})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Recruitments.objects.get().title, "title")
    
    # 없는 동료모집 삭제 실패
    def test_recruitment_delete_fail_not_author(self):
        url = reverse("recruitment_detail_view", kwargs={"recruitment_id": 2})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Recruitments.objects.get().title, "title")


class JoinApplicantTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 유저 3 생성
        cls.user_data3 = {"email": "ccc@ccc.com", "nickname":"ccc", "password": "Test1847!"}
        # cls.user3 = User.objects.create(email="ccc@ccc.com", password="Test1847!", nickname="ccc")
        cls.user3 = User.objects.create(**cls.user_data3)
        cls.user3.set_password("Test1847!")
        cls.user3.save()

        # 동료모집 생성
        cls.recruitment = []
        cls.recruitment.append(Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=2,
            user=cls.user,
            ))
        
        cls.recruitment.append(Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-06-01",
            arrival="2023-06-10",
            cost=5000,
            participant_max=2,
            is_complete = 1,
            user=cls.user,
            ))            

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]        
        self.access_token_3 = self.client.post(reverse("token_obtain_pair"), self.user_data3).data["access"]

    # 동료모집 신청 성공
    def test_applicant_join_success(self):
        response = self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 1}),
            data={
                "appeal":"test appeal"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Applicant.objects.get().appeal, "test appeal")

    # 동료모집 신청 실패 비로그인
    def test_applicant_join_failed_not_logged_in(self):
        response = self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 1}),
            data={
                "appeal":"test appeal"
            },
        )
        self.assertEqual(response.status_code, 401)

    # 동료모집 신청 실패 동료모집 작성자
    def test_applicant_join_failed_author(self):
        response = self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 1}),
            data={
                "appeal":"test appeal"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 204)

    # 동료모집 신청 실패 중복 지원
    def test_applicant_join_failed_participant_over(self):
        self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 1}),
            data={
                "appeal":"test appeal"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        response = self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 1}),
            data={
                "appeal":"test appeal"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Applicant.objects.get().appeal, "test appeal")
        self.assertEqual(Applicant.objects.count(), 1)

    # 동료모집 신청 실패 완료된 모집
    def test_applicant_join_failed_is_complete(self):
        response = self.client.post(
            path=reverse("recruitment_join_view", kwargs={"recruitment_id": 2}),
            data={
                "appeal":"test appeal"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_3}",
        )
        self.assertEqual(response.status_code, 204)


class JoinApplicantEditTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 유저 3 생성
        cls.user_data3 = {"email": "ccc@ccc.com", "nickname":"ccc", "password": "Test1847!"}
        # cls.user3 = User.objects.create(email="ccc@ccc.com", password="Test1847!", nickname="ccc")
        cls.user3 = User.objects.create(**cls.user_data3)
        cls.user3.set_password("Test1847!")
        cls.user3.save()

        # 동료모집 생성
        cls.recruitment = []
        cls.recruitment.append(Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=2,
            user=cls.user,
            ))

        # 동료모집 신청 생성
        cls.applicant = []
        cls.applicant.append(Applicant.objects.create(
            appeal="appeal",
            user=cls.user2,
            recruitment_id=1,
        ))       

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]
        self.access_token_3 = self.client.post(reverse("token_obtain_pair"), self.user_data3).data["access"]

    # 동료모집 신청 수정 성공
    def test_applicant_edit_success(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.put(
            path=url,
            data={
                "appeal":"edit appeal",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Applicant.objects.get().appeal, "edit appeal")

    # 동료모집 신청 수정 실패 비로그인
    def test_applicant_edit_failed_not_logged_in(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.put(
            path=url,
            data={
                "appeal":"edit appeal",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotEqual(Applicant.objects.get().appeal, "edit appeal")

    # 동료모집 신청 수정 실패 다른 유저
    def test_applicant_edit_failed_author(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.put(
            path=url,
            data={
                "appeal":"edit appeal",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_3}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(Applicant.objects.get().appeal, "edit appeal")


class JoinApplicantDeleteTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data3)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 유저 3 생성
        cls.user_data3 = {"email": "ccc@ccc.com", "nickname":"ccc", "password": "Test1847!"}
        # cls.user3 = User.objects.create(email="ccc@ccc.com", password="Test1847!", nickname="ccc")
        cls.user3 = User.objects.create(**cls.user_data3)
        cls.user3.set_password("Test1847!")
        cls.user3.save()

        # 동료모집 생성
        cls.recruitment = []
        cls.recruitment.append(Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=2,
            user=cls.user,
            ))
        
        # 동료모집 신청 생성
        cls.applicant = []
        cls.applicant.append(Applicant.objects.create(
            appeal="appeal",
            user=cls.user2,
            recruitment_id=1,
        ))              

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]
        self.access_token_3 = self.client.post(reverse("token_obtain_pair"), self.user_data3).data["access"]

    # 동료모집 신청 삭제 성공
    def test_applicant_delete_success(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Applicant.objects.count(), 0)

    # 동료모집 신청 삭제 실패 비로그인
    def test_applicant_delete_failed_not_logged_in(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.delete(
            path=url,
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Applicant.objects.count(), 1)

    # 동료모집 신청 삭제 실패 다른 유저
    def test_applicant_delete_failed_author(self):
        url = reverse("applicant_detail_view", kwargs={"applicant_id": 1})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_3}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Applicant.objects.count(), 1)


class AcceptJoinTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()
        
        # 유저 3 생성
        cls.user_data3 = {"email": "ccc@ccc.com", "nickname":"ccc", "password": "Test1847!"}
        # cls.user3 = User.objects.create(email="ccc@ccc.com", password="Test1847!", nickname="ccc")
        cls.user3 = User.objects.create(**cls.user_data3)
        cls.user3.set_password("Test1847!")
        cls.user3.save()

        # 동료모집 생성
        cls.recruitment = []
        recruitment = Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=2,
            user=cls.user,
            )  
        recruitment.participant.set([cls.user])
        cls.recruitment.append(recruitment)
        
        # 동료모집 신청 생성
        cls.applicant = []
        cls.applicant.append(Applicant.objects.create(
            appeal="appeal",
            user=cls.user2,
            recruitment_id=1,
        ))              

        cls.applicant.append(Applicant.objects.create(
            appeal="appeal 2",
            user=cls.user3,
            recruitment_id=1,
        ))


    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]
        self.access_token_3 = self.client.post(reverse("token_obtain_pair"), self.user_data3).data["access"]

    # 동료모집 신청 수락 성공
    def test_applicant_accept_success(self):
        response = self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Recruitments.objects.get().participant.count(), 2)

    # 동료모집 신청 수락 실패 비로그인
    def test_applicant_accept_failed_not_logged_in(self):
        response = self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
        )
        self.assertEqual(response.status_code, 401)

    # 동료모집 신청 수락 실패 다른 유저
    def test_applicant_accept_failed_author(self):
        response = self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_3}",
        )
        self.assertEqual(response.status_code, 403)


    # 동료모집 신청 수락 실패 이미 처리한 유저
    def test_applicant_accept_failed_participant_over(self):
        self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        response = self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 208)
        self.assertEqual(Recruitments.objects.get().participant.count(), 2)


    # 동료모집 신청 수락 실패 마감된 모집
    def test_applicant_accept_failed_is_complete(self):
        self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        response = self.client.post(
            path=reverse("applicant_accept_view", kwargs={"applicant_id": 2}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 208)
        self.assertEqual(Recruitments.objects.get().participant.count(), 2)


class RejectJoinTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 1 생성
        cls.user_data = {"email": "aaa@aaa.com", "nickname":"aaa", "password": "Test1847!"}
        cls.user = User.objects.create_user("aaa@aaa.com", "aaa", "Test1847!")

        # 유저 2 생성
        cls.user_data2 = {"email": "bbb@bbb.com", "nickname":"bbb", "password": "Test1847!"}
        # cls.user2 = User.objects.create(email="bbb@bbb.com", password="Test1847!", nickname="bbb")
        cls.user2 = User.objects.create(**cls.user_data2)
        cls.user2.set_password("Test1847!")
        cls.user2.save()

        # 동료모집 생성
        cls.recruitment = []
        recruitment = Recruitments.objects.create(
            title="title",
            place="place",
            content="content",
            departure="2023-08-01",
            arrival="2023-08-10",
            cost=5000,
            participant_max=2,
            user=cls.user,
            )  
        recruitment.participant.set([cls.user])
        cls.recruitment.append(recruitment)      
        
        # 동료모집 신청 생성
        cls.applicant = []
        cls.applicant.append(Applicant.objects.create(
            appeal="appeal",
            user=cls.user2,
            recruitment_id=1,
        ))              

    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']
        self.access_token_2 = self.client.post(reverse("token_obtain_pair"), self.user_data2).data["access"]

    # 동료모집 신청 거절 성공
    def test_applicant_reject_success(self):
        response = self.client.post(
            path=reverse("applicant_reject_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 동료모집 신청 거절 실패 비로그인
    def test_applicant_reject_failed_not_logged_in(self):
        response = self.client.post(
            path=reverse("applicant_reject_view", kwargs={"applicant_id": 1}),
        )
        self.assertEqual(response.status_code, 401)

    # 동료모집 신청 거절 실패 다른 유저
    def test_applicant_reject_failed_not_author(self):
        response = self.client.post(
            path=reverse("applicant_reject_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_2}",
        )
        self.assertEqual(response.status_code, 403)

    # 동료모집 신청 거절 실패 이미 처리한 신청
    def test_applicant_reject_failed_already_done(self):
        self.client.post(
            path=reverse("applicant_reject_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        response = self.client.post(
            path=reverse("applicant_reject_view", kwargs={"applicant_id": 1}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 204)