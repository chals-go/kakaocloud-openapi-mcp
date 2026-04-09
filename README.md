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

### 방법 1: PyPI에서 설치 (추천)

별도 클론 없이 바로 사용할 수 있습니다.

```bash
# uv가 없다면 먼저 설치
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 확인:
```bash
uvx kakaocloud-openapi-mcp --help
```

### 방법 2: GitHub에서 설치

소스코드를 직접 받아서 사용하거나 수정하고 싶을 때 사용합니다.

```bash
# 저장소 클론
git clone https://github.com/chals-go/kakaocloud-openapi-mcp.git
cd kakaocloud-openapi-mcp

# 의존성 설치
uv sync
```

## MCP 클라이언트 설정

### Claude Code (CLI)

**PyPI 설치 (추천):**
```bash
claude mcp add kakaocloud -- uvx kakaocloud-openapi-mcp
```

**GitHub 설치:**
```bash
claude mcp add kakaocloud -- uv --directory /path/to/kakaocloud-openapi-mcp run kakaocloud-openapi-mcp
```

### Claude Desktop

`claude_desktop_config.json` 파일에 추가:

**PyPI 설치 (추천):**
```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uvx",
      "args": ["kakaocloud-openapi-mcp"]
    }
  }
}
```

**GitHub 설치:**
```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uv",
      "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-openapi-mcp"]
    }
  }
}
```

설정 파일 위치:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### VS Code (Copilot / Continue)

`.vscode/settings.json`에 추가:

**PyPI 설치 (추천):**
```json
{
  "mcp": {
    "servers": {
      "kakaocloud": {
        "command": "uvx",
        "args": ["kakaocloud-openapi-mcp"]
      }
    }
  }
}
```

**GitHub 설치:**
```json
{
  "mcp": {
    "servers": {
      "kakaocloud": {
        "command": "uv",
        "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-openapi-mcp"]
      }
    }
  }
}
```

### Cursor

Cursor Settings > MCP에서 추가하거나, `.cursor/mcp.json`에:

**PyPI 설치 (추천):**
```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uvx",
      "args": ["kakaocloud-openapi-mcp"]
    }
  }
}
```

**GitHub 설치:**
```json
{
  "mcpServers": {
    "kakaocloud": {
      "command": "uv",
      "args": ["--directory", "/path/to/kakaocloud-openapi-mcp", "run", "kakaocloud-openapi-mcp"]
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

## 실제 사용 예시

> 아래는 Claude Code에 이 MCP를 연결한 후 실제로 대화한 내용입니다.

### VM 생성 스크립트 만들기

**사용자 요청:**

```
카카오클라우드에 vm을 만드는 python 스크립트 만들어줘,
test-vpc, test-subnet1에 만들어주고
우분투 24.04, 윈도우 2022 두개 만들거고
vm이름은 test-ubuntu, test-window 로 해줘
그리고 security group은 test-ubuntu-sg, test-window-sg 로 만들고
ubuntu 서버는 22port 인바운드, 윈도우서버는 3389 인바운드 설정되게 해줘
```

**AI가 MCP를 통해 자동으로 수행한 작업:**

1. `get_workflow("VM 인스턴스 생성")` → 인증 → VPC 조회 → 보안 그룹 → 인스턴스 생성 흐름 파악
2. `get_auth_guide()` → IAM 토큰 발급 코드 작성
3. `get_api_detail("bns-vpc", "create-security-group")` → 보안 그룹 생성 파라미터 확인
4. `get_api_detail("bns-vpc", "create-security-group-rule")` → 인바운드 규칙 파라미터 확인
5. `get_api_detail("bcs", "create-instance")` → VM 생성 필수 파라미터 확인

**AI가 생성한 코드:**

<details>
<summary><b>create_vms.py</b> (클릭하여 펼치기)</summary>

```python
"""
카카오클라우드 VM 생성 스크립트
- test-vpc / test-subnet1 에 Ubuntu 24.04, Windows 2022 VM 2대 생성
- 각 VM에 보안 그룹 생성 및 인바운드 규칙 설정
"""

import os
import sys
import requests

# ──────────────────────────────────────────────
# 설정값 (환경변수 또는 직접 입력)
# ──────────────────────────────────────────────
ACCESS_KEY_ID = os.environ.get("KAKAO_ACCESS_KEY_ID", "YOUR_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("KAKAO_SECRET_KEY", "YOUR_SECRET_KEY")

UBUNTU_2404_IMAGE_ID = os.environ.get("UBUNTU_2404_IMAGE_ID", "YOUR_UBUNTU_24.04_IMAGE_ID")
WINDOWS_2022_IMAGE_ID = os.environ.get("WINDOWS_2022_IMAGE_ID", "YOUR_WINDOWS_2022_IMAGE_ID")

KEY_NAME = os.environ.get("KAKAO_KEY_NAME", "YOUR_KEYPAIR_NAME")
FLAVOR = os.environ.get("KAKAO_FLAVOR", "m2a.large")

# ──────────────────────────────────────────────
# API 엔드포인트
# ──────────────────────────────────────────────
IAM_URL = "https://iam.kakaocloud.com/identity/v3/auth/tokens"
BNS_BASE = "https://bns.kr-central-2.kakaocloud.com/api/v1"
BCS_BASE = "https://bcs.kr-central-2.kakaocloud.com/api/v1"

HEADERS = {"Content-Type": "application/json"}


def get_token():
    """IAM 인증 토큰 발급"""
    payload = {
        "auth": {
            "identity": {
                "methods": ["application_credential"],
                "application_credential": {
                    "id": ACCESS_KEY_ID,
                    "secret": SECRET_KEY,
                },
            }
        }
    }
    resp = requests.post(IAM_URL, json=payload, headers=HEADERS)
    resp.raise_for_status()
    token = resp.headers["X-Subject-Token"]
    print("[OK] 토큰 발급 완료")
    return token


def auth_headers(token):
    return {"X-Auth-Token": token, "Content-Type": "application/json"}


def find_vpc(token, name="test-vpc"):
    """VPC 이름으로 ID 조회"""
    resp = requests.get(f"{BNS_BASE}/vpcs", headers=auth_headers(token))
    resp.raise_for_status()
    for vpc in resp.json().get("vpcs", []):
        if vpc.get("name") == name:
            print(f"[OK] VPC 발견: {name} ({vpc['id']})")
            return vpc["id"]
    sys.exit(f"[ERROR] VPC '{name}'을 찾을 수 없습니다.")


def find_subnet(token, name="test-subnet1"):
    """서브넷 이름으로 ID 조회"""
    resp = requests.get(f"{BNS_BASE}/subnets", headers=auth_headers(token))
    resp.raise_for_status()
    for subnet in resp.json().get("subnets", []):
        if subnet.get("name") == name:
            print(f"[OK] Subnet 발견: {name} ({subnet['id']})")
            return subnet["id"]
    sys.exit(f"[ERROR] Subnet '{name}'을 찾을 수 없습니다.")


def create_security_group(token, name, vpc_id, description=""):
    """보안 그룹 생성"""
    payload = {"name": name, "vpc_id": vpc_id, "description": description}
    resp = requests.post(f"{BNS_BASE}/security-groups", json=payload, headers=auth_headers(token))
    resp.raise_for_status()
    sg = resp.json()
    sg_id = sg.get("id") or sg.get("security_group", {}).get("id")
    print(f"[OK] 보안 그룹 생성: {name} ({sg_id})")
    return sg_id


def add_inbound_rule(token, sg_id, port):
    """보안 그룹에 TCP 인바운드 규칙 추가"""
    payload = {
        "direction": "inbound",
        "protocol": "tcp",
        "port_range_min": port,
        "port_range_max": port,
        "remote_ip_prefix": "0.0.0.0/0",
    }
    resp = requests.post(f"{BNS_BASE}/security-groups/{sg_id}/rules", json=payload, headers=auth_headers(token))
    resp.raise_for_status()
    print(f"[OK] 인바운드 규칙 추가: port {port} (0.0.0.0/0)")


def create_instance(token, name, image_id, subnet_id, sg_id, key_name=None):
    """VM 인스턴스 생성"""
    payload = {
        "instance_name": name,
        "image_id": image_id,
        "flavor": FLAVOR,
        "networks": [{"subnet_id": subnet_id, "security_groups": [sg_id]}],
    }
    if key_name:
        payload["key_name"] = key_name

    resp = requests.post(f"{BCS_BASE}/instances", json=payload, headers=auth_headers(token))
    resp.raise_for_status()
    instance = resp.json()
    instance_id = instance.get("id") or instance.get("instance", {}).get("id")
    print(f"[OK] 인스턴스 생성 요청: {name} ({instance_id})")
    return instance_id


def main():
    print("=" * 50)
    print("카카오클라우드 VM 생성 스크립트")
    print("=" * 50)

    # 1. 인증
    token = get_token()

    # 2. VPC / Subnet 조회
    vpc_id = find_vpc(token, "test-vpc")
    subnet_id = find_subnet(token, "test-subnet1")

    # 3. 보안 그룹 생성
    print("\n--- 보안 그룹 생성 ---")
    ubuntu_sg_id = create_security_group(token, "test-ubuntu-sg", vpc_id, "Ubuntu SSH 접근용")
    add_inbound_rule(token, ubuntu_sg_id, 22)

    windows_sg_id = create_security_group(token, "test-window-sg", vpc_id, "Windows RDP 접근용")
    add_inbound_rule(token, windows_sg_id, 3389)

    # 4. VM 인스턴스 생성
    print("\n--- VM 인스턴스 생성 ---")
    ubuntu_id = create_instance(token, "test-ubuntu", UBUNTU_2404_IMAGE_ID, subnet_id, ubuntu_sg_id, KEY_NAME)
    windows_id = create_instance(token, "test-window", WINDOWS_2022_IMAGE_ID, subnet_id, windows_sg_id)

    # 5. 결과 요약
    print("\n" + "=" * 50)
    print("생성 완료 요약")
    print("=" * 50)
    print(f"  Ubuntu VM   : test-ubuntu  ({ubuntu_id})")
    print(f"    - 이미지  : Ubuntu 24.04")
    print(f"    - 보안그룹: test-ubuntu-sg (SSH 22)")
    print(f"  Windows VM  : test-window  ({windows_id})")
    print(f"    - 이미지  : Windows Server 2022")
    print(f"    - 보안그룹: test-window-sg (RDP 3389)")
    print(f"  VPC         : test-vpc ({vpc_id})")
    print(f"  Subnet      : test-subnet1 ({subnet_id})")
    print("=" * 50)
    print("\n※ 인스턴스 생성은 비동기 처리됩니다. 콘솔에서 상태를 확인하세요.")


if __name__ == "__main__":
    main()
```

</details>

**실행 방법:**

```bash
# 환경변수 설정
export KAKAO_ACCESS_KEY_ID="발급받은_ACCESS_KEY_ID"
export KAKAO_SECRET_KEY="발급받은_SECRET_KEY"
export UBUNTU_2404_IMAGE_ID="Ubuntu_24.04_이미지_ID"
export WINDOWS_2022_IMAGE_ID="Windows_2022_이미지_ID"
export KAKAO_KEY_NAME="SSH_키페어_이름"

# 실행
pip install requests
python create_vms.py
```

**스크립트 동작 흐름:**

```
1. IAM 토큰 발급
2. test-vpc, test-subnet1 이름으로 VPC/Subnet ID 조회
3. 보안 그룹 생성
   ├── test-ubuntu-sg → TCP 22 (SSH) 인바운드
   └── test-window-sg → TCP 3389 (RDP) 인바운드
4. VM 인스턴스 생성
   ├── test-ubuntu  — Ubuntu 24.04 + SSH 키페어
   └── test-window  — Windows Server 2022
```

> 사용자는 한 줄의 요청만 했지만, AI가 MCP를 통해 카카오클라우드 API의 인증 방식, 엔드포인트 URL, 파라미터 형식을 자동으로 파악하여 바로 실행 가능한 스크립트를 생성했습니다.

### 다른 요청 예시

```
# VPC 네트워크 구성
"카카오클라우드에서 VPC를 만들고, 퍼블릭/프라이빗 서브넷을 구성하는 코드를 작성해줘."

# Kubernetes 클러스터 배포
"카카오클라우드에서 Kubernetes 클러스터를 생성하고, 워커 노드 3대로 구성하는 스크립트를 만들어줘."

# MySQL 데이터베이스 생성
"카카오클라우드에서 MySQL 8.0 데이터베이스를 생성하는 코드 작성해줘."

# 로드 밸런서 설정
"카카오클라우드에서 로드 밸런서를 만들고 2대의 웹 서버에 트래픽을 분산하는 코드 작성해줘."
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
uv run kakaocloud-openapi-mcp
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
