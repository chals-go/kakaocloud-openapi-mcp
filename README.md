# KakaoCloud OpenAPI MCP Server

카카오클라우드 OpenAPI 문서를 AI 코딩 어시스턴트(Claude Code, Codex 등)에서 쉽게 활용할 수 있도록 하는 MCP(Model Context Protocol) 서버입니다.

## 왜 필요한가?

카카오클라우드에서 VM을 만들거나 VPC를 구성할 때, API 문서를 일일이 찾아가며 코딩하는 것은 번거롭습니다.

이 MCP 서버를 설치하면 AI 어시스턴트가 자동으로 카카오클라우드 API 정보를 조회하여 정확한 코드를 생성해줍니다.

```
사용자: "카카오클라우드에서 VM 만드는 파이썬 스크립트 작성해줘"

AI → MCP 서버에서 VM 생성 API 정보 조회
AI → VPC, Subnet, Security Group, Keypair 등 사전 조건 파악
AI → 인증 방법 포함한 완전한 파이썬 스크립트 생성
```

## 지원 서비스

| 서비스 | 설명 | 엔드포인트 수 |
|--------|------|:------------:|
| **BCS** (Beyond Compute Service) | VM, 볼륨, 이미지, 스냅샷, 키페어 | 53 |
| **VPC** | VPC, 서브넷, 보안 그룹, 라우트 테이블, 공인 IP | 28 |
| **Load Balancer** | 로드 밸런서, 리스너, 대상 그룹 | 6 |
| **Transit Gateway** | VPC 간 네트워크 연결 | 4 |
| **Container Pack** | 관리형 Kubernetes (K8s Engine) | 16 |
| **Data Store** | 관리형 MySQL | 18 |

총 **125개 API 엔드포인트** + **5개 워크플로우** 가이드

## 설치

### 요구 사항

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/chals-go/kakaocloud-openapi-mcp.git
cd kakaocloud-openapi-mcp

# 의존성 설치
uv sync
```

## MCP 클라이언트 설정

### Claude Code (CLI)

```bash
claude mcp add kakaocloud -- uv --directory /path/to/kakaocloud-openapi-mcp run kakaocloud-mcp
```

또는 설정 파일에 직접 추가:

```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uv",
      "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-mcp"]
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json` 파일에 추가:

```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uv",
      "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-mcp"]
    }
  }
}
```

설정 파일 위치:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### VS Code (Copilot / Continue)

`.vscode/settings.json`에 추가:

```json
{
  "mcp": {
    "servers": {
      "kakaocloud": {
        "command": "uv",
        "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-mcp"]
      }
    }
  }
}
```

### Cursor

Cursor Settings > MCP에서 추가하거나, `.cursor/mcp.json`에:

```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uv",
      "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-mcp"]
    }
  }
}
```

## MCP 도구 (Tools)

MCP 서버는 5개의 도구를 제공합니다. AI 어시스턴트가 자동으로 적절한 도구를 선택하여 호출합니다.

### 1. `search_kakaocloud_api`

키워드로 카카오클라우드 API를 검색합니다. 한국어와 영어 모두 지원합니다.

```
입력: { "query": "VM 생성" }
출력: 관련 API 엔드포인트 목록 (서비스, method, path, 설명)
```

**사용 예시:**
- "VM 생성" → BCS 인스턴스 생성 API + 관련 워크플로우
- "load balancer" → 로드 밸런서 관련 API 목록
- "보안 그룹" → VPC 보안 그룹 CRUD API 목록

### 2. `get_api_detail`

특정 API 엔드포인트의 상세 스펙을 조회합니다.

```
입력: { "service": "bcs", "endpoint_id": "create-instance" }
출력: 파라미터, 요청/응답 바디, 전체 URL, 인증 방법, 예제
```

**서비스 별칭 지원:**
- `vm`, `instance`, `compute` → BCS
- `vpc`, `네트워크` → VPC
- `lb`, `로드밸런서` → Load Balancer
- `k8s`, `kubernetes` → Container Pack
- `mysql`, `db` → Data Store

### 3. `get_service_overview`

서비스의 전체 개요와 엔드포인트 목록을 조회합니다.

```
입력: { "service": "vm" }
출력: 서비스 설명, Base URL, 전체 엔드포인트 테이블, 관련 서비스
```

### 4. `get_workflow`

특정 작업의 전체 API 호출 흐름을 단계별로 안내합니다.

```
입력: { "task": "VM 인스턴스 생성" }
출력: 인증 → VPC → 서브넷 → 보안 그룹 → 키페어 → 인스턴스 생성 순서
```

**제공 워크플로우:**
| 워크플로우 | 설명 |
|-----------|------|
| `create-vm` | VM 인스턴스 생성 (VPC/서브넷/보안그룹/키페어 포함) |
| `create-vpc-network` | VPC 네트워크 전체 구성 |
| `setup-load-balancer` | 로드 밸런서 설정 (대상 그룹, 리스너 포함) |
| `create-k8s-cluster` | Kubernetes 클러스터 생성 및 노드 풀 구성 |
| `create-mysql-db` | 관리형 MySQL 데이터베이스 생성 |

### 5. `get_auth_guide`

카카오클라우드 API 인증 방법을 안내합니다.

```
입력: (없음)
출력: 토큰 발급 방법, 코드 예제 (Python, curl), 토큰 사용법
```

## MCP 리소스 (Resources)

정적 참조 데이터를 Resource URI로 조회할 수 있습니다.

| URI | 설명 |
|-----|------|
| `kakaocloud://services` | 전체 서비스 목록 (JSON) |
| `kakaocloud://service/{name}` | 특정 서비스의 전체 API 스펙 (JSON) |
| `kakaocloud://auth` | 인증 가이드 데이터 (JSON) |

## 사용 예시

### 예시 1: VM 만드는 파이썬 스크립트

AI에게 요청:
```
카카오클라우드에서 VM 인스턴스를 만드는 파이썬 스크립트를 작성해줘.
Ubuntu 이미지를 사용하고, m2a.large 타입으로, SSH 접속이 가능하게 해줘.
```

AI가 MCP를 통해 자동으로:
1. `get_workflow("VM 인스턴스 생성")` → 전체 API 호출 흐름 파악
2. `get_auth_guide()` → 인증 코드 작성
3. `get_api_detail("bcs", "create-instance")` → 필수 파라미터 확인
4. 완전한 파이썬 스크립트 생성

### 예시 2: VPC 네트워크 구성

```
카카오클라우드에서 VPC를 만들고, 퍼블릭/프라이빗 서브넷을 구성하는 코드를 작성해줘.
SSH와 HTTP 포트를 여는 보안 그룹도 포함해줘.
```

### 예시 3: Kubernetes 클러스터 배포

```
카카오클라우드에서 Kubernetes 클러스터를 생성하고,
워커 노드 3대로 구성하는 스크립트를 만들어줘.
```

## 개발

### 테스트 실행

```bash
uv run pytest tests/ -v
```

### MCP Inspector로 디버깅

```bash
uv run mcp dev src/kakaocloud_mcp/server.py
```

MCP Inspector가 브라우저에서 열리며, 각 도구를 직접 호출하고 결과를 확인할 수 있습니다.

### 서버 직접 실행

```bash
uv run kakaocloud-mcp
```

서버는 stdio 모드로 동작하므로, MCP 클라이언트가 stdin/stdout을 통해 통신합니다.

### 프로젝트 구조

```
kakaocloud-openapi-mcp/
├── pyproject.toml                    # 프로젝트 설정 및 의존성
├── src/
│   └── kakaocloud_mcp/
│       ├── server.py                 # MCP 서버 진입점
│       ├── tools/                    # MCP Tool 구현
│       │   ├── search.py             # search_kakaocloud_api
│       │   ├── detail.py             # get_api_detail
│       │   ├── overview.py           # get_service_overview
│       │   ├── workflow.py           # get_workflow
│       │   └── auth.py               # get_auth_guide
│       ├── resources/
│       │   └── services.py           # MCP Resource 핸들러
│       ├── data/
│       │   ├── loader.py             # JSON 데이터 로더 + 검색 인덱스
│       │   ├── auth.json             # 인증 가이드 데이터
│       │   ├── workflows.json        # 워크플로우 데이터
│       │   └── services/             # 서비스별 API 스펙 JSON
│       │       ├── bcs.json
│       │       ├── bns-vpc.json
│       │       ├── bns-load-balancer.json
│       │       ├── bns-transit-gateway.json
│       │       ├── container-pack.json
│       │       └── data-store-mysql.json
│       └── utils/
│           └── search.py             # 키워드 검색 유틸리티
└── tests/
    ├── test_search.py                # 검색 + 데이터 로더 테스트
    └── test_tools.py                 # Tool 함수 테스트
```

### API 데이터 추가/수정

각 서비스의 API 스펙은 `src/kakaocloud_mcp/data/services/` 디렉토리의 JSON 파일에 정의됩니다.

새 엔드포인트를 추가하려면:

1. 해당 서비스의 JSON 파일을 열고 `endpoints` 배열에 추가
2. `keywords` 필드에 한국어/영어 검색 키워드를 충분히 포함
3. `uv run pytest tests/ -v` 로 테스트 통과 확인

엔드포인트 구조:
```json
{
  "id": "create-instance",
  "method": "POST",
  "path": "/instances",
  "summary": "VM 인스턴스 생성",
  "summaryKo": "VM 인스턴스 생성",
  "keywords": ["vm 생성", "인스턴스 만들기"],
  "parameters": [],
  "requestBody": { ... },
  "responses": { "202": { "description": "..." } }
}
```

## 참고

- [카카오클라우드 OpenAPI 문서](https://docs.kakaocloud.com/openapi)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io)
- [카카오클라우드 콘솔](https://console.kakaocloud.com)

## 라이선스

MIT License
