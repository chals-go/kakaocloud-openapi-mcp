---
name: api-research
description: "카카오클라우드 OpenAPI 문서를 크롤링하고 API 스펙을 구조화된 형태로 수집하는 스킬. 카카오클라우드 API 조사, 문서 수집, 엔드포인트 파악, 서비스 목록 조사 요청 시 사용."
---

# 카카오클라우드 OpenAPI 문서 조사

카카오클라우드 OpenAPI 문서(https://docs.kakaocloud.com/openapi)를 체계적으로 크롤링하여 MCP 서버에서 활용할 수 있는 구조화된 API 스펙을 생성한다.

## 조사 워크플로우

### Step 1: 서비스 목록 수집

1. https://docs.kakaocloud.com/openapi 메인 페이지를 WebFetch로 가져온다
2. 사이드바 또는 본문에서 서비스 카테고리와 개별 서비스 링크를 추출한다
3. 서비스 목록을 `_workspace/01_api_research/service_list.json`에 저장한다

### Step 2: 서비스별 API 스펙 수집

각 서비스에 대해:

1. 서비스 문서 페이지를 WebFetch로 가져온다
2. API 레퍼런스 페이지(있다면)를 추가로 가져온다
3. 다음 정보를 추출한다:
   - base URL
   - 인증 방식
   - 엔드포인트 목록 (method, path, description)
   - 각 엔드포인트의 파라미터 (필수/선택 구분)
   - 요청/응답 바디 스키마
   - 에러 코드

4. 결과를 `_workspace/01_api_research/{service-name}.json`에 저장한다

### Step 3: 서비스 관계 분석

1. 서비스 간 의존성을 파악한다
   - VM 생성 → VPC, Subnet, Security Group, Key Pair 필요
   - Load Balancer → VPC, Subnet, Target Group 필요
2. 의존성 그래프를 `_workspace/01_api_research/dependencies.json`에 저장한다

### Step 4: 인증 가이드 정리

1. 카카오클라우드 API 인증 방식을 정리한다 (API Key, Access Token 등)
2. 토큰 발급/갱신 API를 포함한다
3. `_workspace/01_api_research/auth.md`에 저장한다

### Step 5: 워크플로우 정리

주요 사용 시나리오별 API 호출 순서를 정리한다:

```json
{
  "workflow": "VM 인스턴스 생성",
  "steps": [
    {"order": 1, "action": "VPC 생성 또는 기존 VPC 조회", "api": "POST /vpcs 또는 GET /vpcs"},
    {"order": 2, "action": "Subnet 생성 또는 조회", "api": "POST /subnets 또는 GET /subnets"},
    {"order": 3, "action": "Security Group 생성", "api": "POST /security-groups"},
    {"order": 4, "action": "Key Pair 생성", "api": "POST /key-pairs"},
    {"order": 5, "action": "VM 인스턴스 생성", "api": "POST /instances"}
  ]
}
```

결과를 `_workspace/01_api_research/workflows.json`에 저장한다.

### Step 6: 요약 보고서 생성

`_workspace/01_api_research/summary.md`에 전체 조사 결과를 요약한다:
- 발견된 서비스 수와 목록
- 서비스별 엔드포인트 수
- 수집 실패/불완전한 서비스 목록
- 주요 워크플로우 목록

## 크롤링 시 주의사항

- robots.txt를 존중한다
- 페이지 간 요청 간격을 두어 서버에 부담을 주지 않는다
- JavaScript 렌더링이 필요한 페이지는 WebFetch로 접근 불가할 수 있다. 이 경우 해당 사실을 기록하고 수동 확인이 필요한 항목으로 표시한다
- OpenAPI/Swagger JSON 스펙 파일이 직접 제공되는 경우 해당 파일을 우선 활용한다
