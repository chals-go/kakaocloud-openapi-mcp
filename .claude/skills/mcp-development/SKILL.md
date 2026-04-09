---
name: mcp-development
description: "카카오클라우드 OpenAPI MCP 서버를 설계하고 구현하는 스킬. MCP 서버 개발, Tool/Resource 구현, 코드 작성, 프로젝트 구조 생성 요청 시 사용."
---

# 카카오클라우드 MCP 서버 개발

수집된 카카오클라우드 OpenAPI 스펙을 기반으로 MCP 서버를 설계하고 구현한다.

## 핵심 설계 원칙

이 MCP 서버의 목적은 API를 직접 호출하는 것이 아니라, AI 코딩 어시스턴트가 카카오클라우드 API를 사용하는 코드를 작성할 때 필요한 정보를 제공하는 것이다.

사용자가 "VM 만드는 파이썬 스크립트 만들어줘"라고 하면:
1. AI가 MCP 도구를 호출하여 VM 생성 관련 API 정보를 받는다
2. 받은 정보를 기반으로 올바른 API 호출 코드를 생성한다

## 기술 스택

- **런타임**: Node.js (TypeScript) 또는 Python
- **MCP SDK**: `@modelcontextprotocol/sdk` (TS) 또는 `mcp` (Python)
- **데이터 저장**: 구조화된 JSON 파일 (별도 DB 불필요)

## MCP Tool 설계

### 1. search_kakaocloud_api

키워드로 관련 API를 검색한다.

```
입력: { query: "VM 생성" }
출력: 관련 API 엔드포인트 목록 + 간단한 설명
```

### 2. get_api_detail

특정 API의 상세 스펙을 조회한다.

```
입력: { service: "virtual-machine", endpoint: "/instances", method: "POST" }
출력: 파라미터, 요청/응답 바디, 인증 방식, 예제 코드
```

### 3. get_service_overview

서비스 전체 개요와 엔드포인트 목록을 조회한다.

```
입력: { service: "virtual-machine" }
출력: 서비스 설명, 엔드포인트 목록, 관련 서비스
```

### 4. get_workflow

특정 작업의 전체 API 호출 흐름을 조회한다.

```
입력: { task: "VM 인스턴스 생성" }
출력: 순서대로 호출해야 할 API 목록 + 각 단계 설명
```

### 5. get_auth_guide

카카오클라우드 API 인증 방법을 안내한다.

```
입력: {}
출력: 인증 방식, 토큰 발급 API, 코드 예제
```

## MCP Resource 설계

정적 참조 데이터를 Resource로 제공한다:

- `kakaocloud://services` - 전체 서비스 목록
- `kakaocloud://service/{name}` - 서비스별 전체 API 스펙
- `kakaocloud://auth` - 인증 가이드

## 프로젝트 구조

```
kakaocloud-openapi-mcp/
  src/
    index.ts              # MCP 서버 진입점
    tools/
      search.ts           # search_kakaocloud_api 구현
      detail.ts           # get_api_detail 구현
      overview.ts         # get_service_overview 구현
      workflow.ts         # get_workflow 구현
      auth.ts             # get_auth_guide 구현
    resources/
      services.ts         # Resource 핸들러
    data/
      services/           # 서비스별 API 스펙 JSON
      workflows.json      # 워크플로우 데이터
      auth.json           # 인증 정보
    utils/
      search.ts           # 검색 유틸리티
  package.json
  tsconfig.json
  README.md
```

## 구현 순서

1. 프로젝트 초기화 (package.json, tsconfig.json)
2. MCP 서버 기본 틀 구현 (index.ts)
3. 데이터 파일 배치 (`_workspace/01_api_research/`에서 `src/data/`로)
4. Tool 구현 (search → detail → overview → workflow → auth 순)
5. Resource 구현
6. 검색 기능 구현 (키워드 매칭)

## 코드 품질 기준

- 모든 Tool의 입력 파라미터에 JSON Schema validation을 적용한다
- 에러 응답에 사용자 친화적 메시지를 포함한다
- 데이터 파일 로딩 실패 시 graceful degradation한다
