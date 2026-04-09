# 카카오클라우드 OpenAPI 문서 구조 참조

이 파일은 카카오클라우드 OpenAPI 문서의 알려진 구조를 정리한다.
API 조사 시 이 정보를 출발점으로 활용하되, 실제 문서와 다를 수 있으므로 항상 최신 문서를 확인한다.

## 문서 URL 구조

- 메인: https://docs.kakaocloud.com/openapi
- 서비스별: https://docs.kakaocloud.com/openapi/{service-name}

## 알려진 서비스 카테고리

### Compute
- Beyond Compute Service (가상 머신): 인스턴스 생성/관리, 볼륨, 이미지 템플릿

### Networking
- VPC (Virtual Private Cloud)
- Load Balancing
- Transit Gateway

### Container
- Container Pack (컨테이너 오케스트레이션)

### Storage
- Data Store (데이터 저장)

## API 특성

- RESTful API 설계
- JSON 요청/응답 형식
- 서비스별 base URL이 다를 수 있음

## 주의사항

- 문서는 한국어로 작성되어 있음
- JavaScript 렌더링이 필요한 페이지가 있을 수 있음 (SPA 구조)
- OpenAPI/Swagger 스펙 파일이 별도로 제공될 수 있음 — 발견 시 우선 활용
- 문서 구조가 변경될 수 있으므로 크롤링 시 유연하게 대응
