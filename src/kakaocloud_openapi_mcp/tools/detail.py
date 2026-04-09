"""get_api_detail - 특정 API 엔드포인트의 상세 스펙을 조회한다."""

from __future__ import annotations

import json

from kakaocloud_openapi_mcp.data.loader import get_store


def get_api_detail(service: str, endpoint_id: str) -> str:
    """특정 카카오클라우드 API 엔드포인트의 상세 스펙을 조회한다.

    Args:
        service: 서비스 ID 또는 별칭 (예: "bcs", "vm", "vpc")
        endpoint_id: 엔드포인트 ID (예: "create-instance", "list-volumes")
    """
    store = get_store()
    svc = store.get_service(service)

    if not svc:
        available = ", ".join(sorted(store.services.keys()))
        return f"서비스 '{service}'를 찾을 수 없습니다. 사용 가능한 서비스: {available}"

    ep = store.get_endpoint(service, endpoint_id)
    if not ep:
        ep_ids = [e["id"] for e in svc.get("endpoints", [])]
        return (
            f"엔드포인트 '{endpoint_id}'를 찾을 수 없습니다.\n"
            f"'{svc['id']}' 서비스의 엔드포인트 목록: {', '.join(ep_ids)}"
        )

    lines: list[str] = []
    lines.append(f"# {ep.get('summary', ep['id'])}\n")
    lines.append(f"**서비스:** {svc.get('nameKo', svc['name'])} (`{svc['id']}`)")
    lines.append(f"**메서드:** `{ep['method']}`")
    lines.append(f"**경로:** `{ep['path']}`")
    lines.append(f"**전체 URL:** `{svc.get('baseUrl', '')}{svc.get('basePath', '')}{ep['path']}`\n")

    if ep.get("description"):
        lines.append(f"{ep['description']}\n")

    # Path Parameters
    path_params = [p for p in ep.get("parameters", []) if p.get("in") == "path"]
    if path_params:
        lines.append("## Path Parameters\n")
        for p in path_params:
            req = "필수" if p.get("required") else "선택"
            lines.append(f"- `{p['name']}` ({p.get('type', 'string')}, {req}): {p.get('description', '')}")
        lines.append("")

    # Query Parameters
    query_params = [p for p in ep.get("parameters", []) if p.get("in") == "query"]
    if query_params:
        lines.append("## Query Parameters\n")
        for p in query_params:
            req = "필수" if p.get("required") else "선택"
            lines.append(f"- `{p['name']}` ({p.get('type', 'string')}, {req}): {p.get('description', '')}")
        lines.append("")

    # Request Body
    if ep.get("requestBody"):
        lines.append("## Request Body\n")
        lines.append("```json")
        lines.append(json.dumps(ep["requestBody"], indent=2, ensure_ascii=False))
        lines.append("```\n")

    # Example Request
    if ep.get("exampleRequest"):
        lines.append("## 요청 예시\n")
        lines.append("```json")
        lines.append(json.dumps(ep["exampleRequest"], indent=2, ensure_ascii=False))
        lines.append("```\n")

    # Responses
    if ep.get("responses"):
        lines.append("## 응답\n")
        for code, resp in ep["responses"].items():
            lines.append(f"**{code}**: {resp.get('description', '')}")
            if resp.get("example"):
                lines.append("```json")
                lines.append(json.dumps(resp["example"], indent=2, ensure_ascii=False))
                lines.append("```")
        lines.append("")

    # 인증 안내
    lines.append("## 인증\n")
    lines.append("`X-Auth-Token` 헤더에 IAM 토큰을 포함해야 합니다.")
    lines.append("`get_auth_guide()` 도구로 토큰 발급 방법을 확인하세요.")

    return "\n".join(lines)
