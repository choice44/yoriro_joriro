from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from spots.models import Area, Sigungu, Spot

from faker import Faker
import random


class SpotsReadTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.areas = []
        for _ in range(10):
            cls.areas.append(Area.objects.create(
                name=cls.faker.city()
            ))

        cls.sigungus = []
        for _ in range(10):
            cls.sigungus.append(Sigungu.objects.create(
                area=random.choice(cls.areas),
                code=random.randrange(1, 10),
                name=cls.faker.city_suffix()
            ))

        cls.spots = []
        for _ in range(10):
            cls.spots.append(Spot.objects.create(
                area=random.choice(cls.areas),
                type=random.choice([12, 39]),
                sigungu=random.randrange(1, 10),
                addr1=cls.faker.address(),
                mapx=cls.faker.coordinate(),
                mapy=cls.faker.coordinate(),
                firstimage=cls.faker.url(),
                tel=cls.faker.phone_number()
            ))

    # 지역 전체 목록 조회 성공
    # view = AreaView, url name = "area_view", method = get
    def test_pass_area_list(self):
        response = self.client.get(path=reverse("area_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for (data, area) in zip(response.data, self.areas):
            self.assertEqual(data['name'], area.name)

    # 지역 전체 목록 조회 성공
    # view = SigunguView, url name = "sigungu_view", method = get
    def test_pass_sigungu_list(self):
        for area in self.areas:
            url = area.get_absolute_url()
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for (data, sigungu) in zip(response.data, [x for x in self.sigungus if x.area == area]):
                self.assertEqual(data['name'], sigungu.name)
                self.assertEqual(data['code'], sigungu.code)

    # 스팟 전체 목록 조회 성공
    # view = SpotFilterView, url name = "spot_view", method = get
    def test_pass_spot_list(self):
        response = self.client.get(path=reverse("spot_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for (data, spot) in zip(response.data['results'], self.spots):
            self.assertEqual(data['area'], spot.area.id)
            self.assertEqual(data['type'], spot.type)
            self.assertEqual(data['sigungu'], spot.sigungu)
            self.assertEqual(data['addr1'], spot.addr1)
            self.assertEqual(data['mapx'], float(spot.mapx))
            self.assertEqual(data['mapy'], float(spot.mapy))
            self.assertEqual(data['firstimage'], spot.firstimage)
            self.assertEqual(data['tel'], spot.tel)

    # 스팟 상세 정보 조회 성공
    # view = SpotDetailView, url name = "spot_detail_view", method = get
    def test_pass_spot_detail(self):
        for spot in self.spots:
            url = spot.get_absolute_url()
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['area'], spot.area.id)
            self.assertEqual(response.data['type'], spot.type)
            self.assertEqual(response.data['sigungu'], spot.sigungu)
            self.assertEqual(response.data['addr1'], spot.addr1)
            self.assertEqual(response.data['mapx'], float(spot.mapx))
            self.assertEqual(response.data['mapy'], float(spot.mapy))
            self.assertEqual(response.data['firstimage'], spot.firstimage)
            self.assertEqual(response.data['tel'], spot.tel)
