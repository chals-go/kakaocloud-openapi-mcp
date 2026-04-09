"""get_service_overview - 서비스 전체 개요와 엔드포인트 목록을 조회한다."""

from __future__ import annotations

from kakaocloud_mcp.data.loader import get_store


def get_service_overview(service: str) -> str:
    """카카오클라우드 서비스의 전체 개요와 엔드포인트 목록을 조회한다.

    Args:
        service: 서비스 ID 또는 별칭 (예: "bcs", "vm", "vpc", "lb", "mysql")
    """
    store = get_store()
    svc = store.get_service(service)

    if not svc:
        available = ", ".join(sorted(store.services.keys()))
        return f"서비스 '{service}'를 찾을 수 없습니다. 사용 가능한 서비스: {available}"

    lines: list[str] = []
    lines.append(f"# {svc.get('nameKo', svc['name'])} ({svc['id']})\n")
    lines.append(f"{svc.get('description', '')}\n")
    lines.append(f"**Base URL:** `{svc.get('baseUrl', '')}{svc.get('basePath', '')}`\n")

    # 의존 서비스
    deps = svc.get("dependencies", [])
    if deps:
        dep_names = []
        for dep_id in deps:
            dep_svc = store.services.get(dep_id)
            if dep_svc:
                dep_names.append(f"{dep_svc.get('nameKo', dep_id)} (`{dep_id}`)")
            else:
                dep_names.append(f"`{dep_id}`")
        lines.append(f"**관련 서비스:** {', '.join(dep_names)}\n")

    # 엔드포인트 목록
    endpoints = svc.get("endpoints", [])
    if endpoints:
        lines.append(f"## 엔드포인트 ({len(endpoints)}개)\n")
        lines.append("| 메서드 | 경로 | 설명 | ID |")
        lines.append("|--------|------|------|----|")
        for ep in endpoints:
            lines.append(
                f"| `{ep['method']}` | `{ep['path']}` | "
                f"{ep.get('summary', '')} | `{ep['id']}` |"
            )
        lines.append("")

    lines.append(
        "> 상세 정보는 `get_api_detail(service=\""
        + svc["id"]
        + '", endpoint_id="<ID>")` 로 조회하세요.'
    )

    return "\n".join(lines)
