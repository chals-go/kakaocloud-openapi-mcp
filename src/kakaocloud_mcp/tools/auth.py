"""get_auth_guide - 카카오클라우드 API 인증 가이드를 제공한다."""

from __future__ import annotations

import json

from kakaocloud_mcp.data.loader import get_store


def get_auth_guide() -> str:
    """카카오클라우드 API 인증 방법, 토큰 발급, 코드 예제를 반환한다."""
    store = get_store()
    auth = store.auth

    if not auth:
        return "인증 가이드 데이터가 아직 준비되지 않았습니다."

    lines: list[str] = []
    lines.append("# 카카오클라우드 API 인증 가이드\n")
    lines.append(f"{auth.get('overview', '')}\n")

    # 토큰 발급 엔드포인트
    lines.append(f"**토큰 발급 엔드포인트:** `{auth.get('tokenEndpoint', '')}`\n")

    # 인증 방법들
    for method in auth.get("methods", []):
        lines.append(f"## {method['name']}\n")
        if method.get("description"):
            lines.append(f"{method['description']}\n")

        lines.append(f"**HTTP 메서드:** `POST`")
        lines.append(f"**URL:** `{auth.get('tokenEndpoint', '')}`")
        lines.append(f"**Content-Type:** `application/json`\n")

        if method.get("requestBody"):
            lines.append("**Request Body:**")
            lines.append("```json")
            lines.append(json.dumps(method["requestBody"], indent=2, ensure_ascii=False))
            lines.append("```\n")

        lines.append(f"**응답 헤더:** `{method.get('responseHeader', 'X-Subject-Token')}` — 발급된 토큰")
        lines.append(f"**토큰 유효 기간:** {method.get('tokenValidity', '12시간')}\n")

        usage = method.get("usage", {})
        if usage:
            lines.append("**토큰 사용 방법:**")
            lines.append(f"요청 헤더에 `{usage.get('headerName', 'X-Auth-Token')}: {{토큰값}}` 추가\n")

    # 프로젝트 조회
    proj = auth.get("projectListEndpoint")
    if proj:
        lines.append("## 프로젝트 목록 조회\n")
        lines.append(f"**{proj['method']}** `{proj['url']}`")
        lines.append("헤더: `X-Auth-Token: {{토큰값}}`\n")

    # 코드 예제
    examples = auth.get("codeExamples", {})
    for lang, code in examples.items():
        lines.append(f"## 코드 예제 ({lang})\n")
        lines.append(f"```{lang}")
        lines.append(code)
        lines.append("```\n")

    return "\n".join(lines)
