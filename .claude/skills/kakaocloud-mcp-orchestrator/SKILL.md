---
name: kakaocloud-mcp-orchestrator
description: "카카오클라우드 OpenAPI MCP 서버 개발을 조율하는 오케스트레이터. 카카오클라우드 MCP 개발, API 수집 및 MCP 구현, MCP 서버 만들기 요청 시 사용. 후속 작업: MCP 수정, API 추가 수집, 서비스 추가, MCP 업데이트, 다시 실행, 테스트 재실행, 이전 결과 개선, 부분 재빌드 요청 시에도 반드시 이 스킬을 사용."
---

# 카카오클라우드 MCP 오케스트레이터

카카오클라우드 OpenAPI 문서를 수집하고 MCP 서버를 개발하는 전체 파이프라인을 조율하는 통합 스킬.

## 실행 모드: 서브 에이전트

## 에이전트 구성

| 에이전트 | 에이전트 정의 | 역할 | 스킬 | 출력 |
|---------|-------------|------|------|------|
| api-researcher | `.claude/agents/api-researcher.md` | API 문서 크롤링/구조화 | api-research | `_workspace/01_api_research/` |
| mcp-developer | `.claude/agents/mcp-developer.md` | MCP 서버 구현 | mcp-development | 프로젝트 루트 소스코드 |
| mcp-tester | `.claude/agents/mcp-tester.md` | MCP 도구 검증 | - | `_workspace/03_test_results/` |

## 워크플로우

### Phase 0: 컨텍스트 확인

1. `_workspace/` 디렉토리 존재 여부를 확인한다
2. 실행 모드를 결정한다:
   - **`_workspace/` 미존재** → 초기 실행. Phase 1로 진행
   - **`_workspace/` 존재 + 사용자가 부분 수정 요청** → 부분 재실행. 해당 에이전트만 재호출
     - "API 추가 수집" → api-researcher만 재호출
     - "MCP 코드 수정" → mcp-developer만 재호출
     - "테스트 다시" → mcp-tester만 재호출
   - **`_workspace/` 존재 + 새 전체 실행 요청** → `_workspace/`를 `_workspace_{timestamp}/`로 이동 후 Phase 1 진행
3. 기존 프로젝트 소스코드(src/) 존재 여부도 확인하여 mcp-developer에게 전달한다

### Phase 1: 준비

1. 사용자 입력을 분석한다:
   - 전체 서비스 수집인지 특정 서비스만인지 파악
   - MCP 서버 기술 스택 선호도 확인 (TypeScript/Python, 기본값: TypeScript)
   - 특별한 요구사항 파악
2. `_workspace/` 디렉토리를 생성한다
3. 입력 분석 결과를 `_workspace/00_input/requirements.md`에 저장한다

### Phase 2: API 문서 수집

api-researcher 에이전트를 호출하여 카카오클라우드 OpenAPI 문서를 수집한다.

```
Agent(
  description: "카카오클라우드 API 문서 수집",
  prompt: "<api-researcher.md의 역할 설명>
    
    api-research 스킬(.claude/skills/api-research/SKILL.md)을 읽고 따르라.
    
    조사 대상: <Phase 1에서 결정된 서비스 목록>
    출력 위치: _workspace/01_api_research/
    
    이전 산출물이 있다면 읽고 개선점을 반영하라.",
  model: "opus"
)
```

**완료 확인:**
- `_workspace/01_api_research/summary.md` 존재 확인
- 최소 1개 이상의 서비스 JSON 파일 존재 확인
- 수집 실패 서비스가 있다면 기록 확인

### Phase 3: MCP 서버 개발

mcp-developer 에이전트를 호출하여 MCP 서버를 구현한다.

```
Agent(
  description: "카카오클라우드 MCP 서버 구현",
  prompt: "<mcp-developer.md의 역할 설명>
    
    mcp-development 스킬(.claude/skills/mcp-development/SKILL.md)을 읽고 따르라.
    
    API 스펙 데이터: _workspace/01_api_research/
    기술 스택: <Phase 1에서 결정된 스택>
    요구사항: _workspace/00_input/requirements.md
    
    프로젝트 루트에 MCP 서버 코드를 생성하라.
    기존 코드가 있다면 읽고 수정/개선하라.",
  model: "opus"
)
```

**완료 확인:**
- package.json (또는 pyproject.toml) 존재 확인
- MCP 서버 진입점 파일 존재 확인
- 최소 1개 Tool 구현 확인

### Phase 4: 테스트 및 검증

mcp-tester 에이전트를 호출하여 MCP 서버를 검증한다.

```
Agent(
  description: "카카오클라우드 MCP 서버 테스트",
  prompt: "<mcp-tester.md의 역할 설명>
    
    테스트 대상: 프로젝트 루트의 MCP 서버 코드
    원본 API 스펙: _workspace/01_api_research/
    
    다음을 검증하라:
    1. 서버가 정상 빌드/시작되는지
    2. 모든 Tool이 올바른 스키마로 노출되는지
    3. 각 Tool에 테스트 입력을 넣어 합리적 결과가 나오는지
    4. 실제 사용 시나리오 테스트 (VM 생성, VPC 구성 등)
    
    결과를 _workspace/03_test_results/test_report.md에 저장하라.",
  model: "opus"
)
```

**완료 확인:**
- `_workspace/03_test_results/test_report.md` 존재 확인
- 테스트 결과 요약 확인

### Phase 5: 수정 반복 (필요 시)

테스트에서 FAIL 항목이 있으면:

1. 테스트 보고서를 분석하여 수정 범위를 판단한다
2. mcp-developer를 재호출하여 수정한다:
   ```
   Agent(
     description: "MCP 서버 버그 수정",
     prompt: "테스트 보고서(_workspace/03_test_results/test_report.md)를 읽고
       FAIL 항목을 수정하라. 수정 후 해당 부분만 재테스트하라.",
     model: "opus"
   )
   ```
3. 최대 2회 반복 후 남은 이슈는 사용자에게 보고한다

### Phase 6: 정리 및 보고

1. `_workspace/` 디렉토리를 보존한다 (삭제하지 않음)
2. 사용자에게 최종 결과를 요약 보고한다:
   - 수집된 서비스 수
   - 구현된 MCP Tool/Resource 목록
   - 테스트 결과 요약
   - 사용 방법 안내 (MCP 설정 방법)

## 데이터 흐름

```
[오케스트레이터]
    │
    ├── Phase 2: Agent(api-researcher)
    │       └── _workspace/01_api_research/ (API 스펙)
    │
    ├── Phase 3: Agent(mcp-developer)
    │       ├── 입력: _workspace/01_api_research/
    │       └── 출력: 프로젝트 루트 소스코드 (src/, package.json 등)
    │
    ├── Phase 4: Agent(mcp-tester)
    │       ├── 입력: 소스코드 + _workspace/01_api_research/
    │       └── 출력: _workspace/03_test_results/
    │
    └── Phase 5: Agent(mcp-developer) [조건부 재호출]
            ├── 입력: _workspace/03_test_results/
            └── 출력: 수정된 소스코드
```

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| API 문서 크롤링 실패 (전체) | 사용자에게 알리고 수동 입력 요청. 문서 URL이 변경되었을 수 있음 |
| API 문서 크롤링 부분 실패 | 성공한 서비스로 진행, 실패 서비스 목록 보고 |
| MCP 서버 빌드 실패 | mcp-developer 재호출 (에러 로그 포함). 1회 재시도 후 실패 시 사용자에게 보고 |
| 테스트 전체 실패 | 서버 코드의 근본적 문제. mcp-developer에게 에러 로그와 함께 전면 수정 요청 |
| 테스트 부분 실패 | Phase 5 수정 반복 실행 |

## 테스트 시나리오

### 정상 흐름
1. 사용자가 "카카오클라우드 MCP 만들어줘" 요청
2. Phase 1: TypeScript 기본 스택으로 전체 서비스 수집 결정
3. Phase 2: api-researcher가 10+ 서비스 API 스펙 수집
4. Phase 3: mcp-developer가 5개 Tool + 3개 Resource 구현
5. Phase 4: mcp-tester가 구조/기능/시나리오 테스트 실행, 대부분 PASS
6. Phase 6: 결과 요약 보고 + MCP 설정 가이드 제공

### 에러 흐름
1. Phase 2에서 카카오클라우드 문서 일부 접근 불가
2. 접근 가능한 서비스(5개)로 Phase 3 진행
3. Phase 4에서 search_api 도구의 검색 결과 부정확 발견
4. Phase 5에서 mcp-developer 재호출하여 검색 로직 수정
5. 재테스트 PASS 후 Phase 6 진행, 미수집 서비스 목록 보고

### 부분 재실행 흐름
1. 사용자가 "VM 서비스 API만 다시 수집해줘" 요청
2. Phase 0에서 부분 재실행 결정
3. api-researcher만 재호출 (VM 서비스 대상)
4. 기존 MCP 코드에 업데이트된 데이터 반영 필요 여부 판단
5. 필요 시 mcp-developer 재호출
