# 요리로 조리로
</br>

## 팀명: 트래블러
</br>

### 리더: 최승원
### 부리더: 장우석
### 팀원: 서지인
### 팀원: 이도윤
### 팀원: 이찬주
<br>

## 서비스 소개
<br>

### 관광지나 맛집의 정보를 가져와 리뷰를 작성하고 스스로 생각한 여행 루트를 공유하는 서비스
<br>

## 주요 기능
<br>

### 회원 기능
#### - JWT 토큰 기반 로그인
#### - 카카오 구글 소셜 로그인
<br>

### 루트 공유
#### - 사용자들이 스스로 생각한 여행 경로를 공유하고, 다른 사용자들의 평점을 받아볼 수 있습니다.
#### - 카카오 맵 API (https://apis.map.kakao.com/) 를 이용해 지도에 경로를 표시할 수 있습니다.
<br>

### 맛집/관광지 리뷰 작성
#### - Tour API (https://api.visitkorea.or.kr/) 의 데이터를 기반으로 등록된 관광지/맛집에 대한 리뷰를 남길 수 있습니다.
<br>

### 여행 동료 모집
#### - 혼자 여행가기 심심한 사용자들이 같이 여행을 갈 동료를 모집할 수 있습니다.
<br>

### 조리로 AI
#### - 사용자들이 업로드 한 이미지에서 인물 영역을 분리해 배경과 합성해주는 AI입니다.
<br>

## 개발환경
<br>

### Python = 3.11.3 
### Django = 4.2.2
### djangorestframework = 3.14.0
### djangorestframework-simplejwt = 5.2.2
### dj-rest-auth = 4.0.1
### django-allauth = 0.51.0
### django-filter = 23.2
### django-cors-headers = 4.0.0
### torch = 2.0.1
### torchaudio = 2.0.2
### torchvision = 0.15.2
### numpy = 1.24.3
### opencv-python = 4.7.0.72
### Pillow = 9.5.0
<br>

## 설치 및 사용방법
### 1. 패키지 설치
- 프로젝트 폴더를 설치하신 후 프로그램 실행에 필요한 패키지들을 설치해주셔야 합니다.
- 터미널에 `pip install -r requirements` 명령어를 통해 필요한 패키지를 한 번에 설치할 수 있습니다.

### 2. 마이그레이션
- 패키지 설치 후 DB에 모델의 내용을 적용시키기 위해 Django의 마이그레이션 기능이 필요합니다.
- `python manage.py makemigrations` 명령어를 통해 마이그레이션을 생성해주고
- `python manage.py migrate` 명령어를 통해 마이그레이션을 적용해줍니다.

### 3. DB에 데이터 저장
- 프로젝트 최상위 폴더에 있는 3개의 json파일(area_data, sigungu_data, spot_data)을 DB에 저장시켜야 합니다.
- 이 json파일들은 각각 시/도, 시군구, 관광지와 맛집의 정보를 담고 있습니다.
- 아래의 명령어를 반드시! 순서대로 하나씩 기입해주세요. 마지막 spot_data의 경우 데이터양이 많아서 다소 시간이 걸릴 수 있습니다.
  ```
  python manage.py loaddata area_data
  python manage.py loaddata sigungu_data
  python manage.py loaddata spot_data
  ```
### 4. 서버 실행
- `python manage.py runserver` 명령어로 서버를 실행시켜주면 끝입니다.

## 팀 노션
<br>

### 팀 노션에서 ERD 설계, 와이어 프레임, API 명세를 확인할 수 있습니다.
### https://lavender-ketch-bb1.notion.site/8d02e4ab946d413a911ecbf826158a3e?pvs=4
<br>

## 프론트 엔드 저장소
<br>

### https://github.com/jeanallen928/yoriro_joriro_front
