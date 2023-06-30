from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class SignupTest(APITestCase):
    # 회원가입 테스트
    def test_signup(self):
        url = reverse("user_view")
        user_data = {
            "email": "test@gmail.com",
            "nickname": "test",
            "password": "12345",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.data["message"], "회원가입 완료!")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserTest(APITestCase):
    def setUp(self):
        self.data = {"email": "test@gmail.com", "nickname": "test", "password": "12345"}
        self.user = User.objects.create_user("test@gmail.com", "test", "12345")
        self.user.set_password("12345")
        self.user.save()

        self.user2 = User.objects.create_user("test2@gmail.com", "test2", "12345")
        self.user2.set_password("12345")
        self.user2.save()

    # 로그인 테스트
    def test_login(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 마이페이지 조회 테스트
    def test_mypage_get(self):
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data[
            "access"
        ]
        user_id = self.user.id
        response = self.client.get(
            reverse("mypage_view", kwargs={"user_id": user_id}),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 마이페이지 수정 테스트
    def test_mypage_put(self):
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data[
            "access"
        ]
        user_id = self.user.id

        response = self.client.get(
            reverse("mypage_view", kwargs={"user_id": user_id}),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        url = reverse("mypage_view", kwargs={"user_id": user_id})

        updated_data = {
            "nickname": "new_nickname",
            "bio": "New bio",
            "gender": "M",
            "age": 30,
        }

        response = self.client.put(
            url,
            data=updated_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        user = User.objects.get(id=user_id)
        self.assertEqual(response.data["message"], "마이페이지 수정 완료!")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 다른 회원이 회원 수정을 시도할 때 실패하는 지
    def test_mypage_put_forbidden(self):
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data[
            "access"
        ]
        user_id = self.user2.id

        url = reverse("mypage_view", kwargs={"user_id": user_id})

        updated_data = {
            "nickname": "new_nickname",
            "bio": "New bio",
            "gender": "M",
            "age": 30,
        }

        response = self.client.put(
            url,
            data=updated_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.data["message"], "권한이 없습니다.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 회원 탈퇴 테스트
    def test_mypage_delete(self):
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data[
            "access"
        ]
        user_id = self.user.id

        response = self.client.delete(
            reverse("mypage_view", kwargs={"user_id": user_id}),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        self.assertEqual(response.data["message"], "회원 탈퇴 완료!")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 다른 회원이 회원 탈퇴를 시도할 때 실패하는 지
    def test_mypage_delete_forbidden(self):
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data[
            "access"
        ]
        user_id = self.user2.id

        url = reverse("mypage_view", kwargs={"user_id": user_id})

        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        self.assertEqual(response.data["message"], "권한이 없습니다.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 마이페이지 수정 테스트 (로그인x)
    def test_mypage_put_unauthenticated(self):
        user_id = self.user.id
        url = reverse("mypage_view", kwargs={"user_id": user_id})

        updated_data = {
            "nickname": "new_nickname",
            "bio": "New bio",
            "gender": "M",
            "age": 30,
        }

        response = self.client.put(
            url,
            data=updated_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 회원 탈퇴 테스트 (로그인x)
    def test_mypage_delete_unauthenticated(self):
        user_id = self.user.id

        response = self.client.delete(
            reverse("mypage_view", kwargs={"user_id": user_id}),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FollowTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", nickname="user1", password="password1"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", nickname="user2", password="password2"
        )

    # 팔로우 테스트
    def test_follow(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow_view", args=[self.user2.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "팔로우하셨습니다.")
        self.assertIn(self.user1, self.user2.followers.all())

    # 언팔로우 테스트
    def test_unfollow(self):
        self.user2.followers.add(self.user1)
        self.client.force_authenticate(user=self.user1)

        url = reverse("follow_view", args=[self.user2.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "언팔로우하셨습니다.")
        self.assertNotIn(self.user1, self.user2.followers.all())

    # 스스로 팔로우할 수 없는 지 테스트
    def test_follow_self(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow_view", args=[self.user1.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "스스로 팔로우할 수 없습니다.")
        self.assertNotIn(self.user1, self.user1.followers.all())

    # 팔로우 테스트 (로그인 x)
    def test_follow_unauthenticated(self):
        url = reverse("follow_view", args=[self.user2.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 언팔로우 테스트 (로그인 x)
    def test_unfollow_unauthenticated(self):
        self.user2.followers.add(self.user1)
        url = reverse("follow_view", args=[self.user2.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 스스로 팔로우할 수 없는 지 테스트 (로그인 x)
    def test_follow_self_unauthenticated(self):
        url = reverse("follow_view", args=[self.user1.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
