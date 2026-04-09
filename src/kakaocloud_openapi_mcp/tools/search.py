"""search_kakaocloud_api - 키워드로 카카오클라우드 API를 검색한다."""

from __future__ import annotations

from kakaocloud_openapi_mcp.data.loader import get_store
from kakaocloud_openapi_mcp.utils.search import search


def search_kakaocloud_api(query: str) -> str:
    """카카오클라우드 API를 키워드로 검색하여 관련 엔드포인트 목록을 반환한다.

    Args:
        query: 검색어 (예: "VM 생성", "로드밸런서", "vpc subnet")
    """
    store = get_store()
    results = search(query, store.search_index, limit=15)

    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다. 다른 키워드로 시도해 주세요."

    lines: list[str] = [f"## 검색 결과: '{query}'\n"]

    for r in results:
        entry = r.entry
        if entry.entry_type == "endpoint":
            svc = store.services.get(entry.service_id, {})
            svc_name = svc.get("nameKo", svc.get("name", entry.service_id))
            lines.append(
                f"- **{entry.method} {entry.path}** ({svc_name})\n"
                f"  {entry.summary}\n"
                f"  서비스: `{entry.service_id}`, 엔드포인트 ID: `{entry.endpoint_id}`\n"
            )
        elif entry.entry_type == "service":
            svc = store.services.get(entry.service_id, {})
            ep_count = len(svc.get("endpoints", []))
            lines.append(
                f"- **서비스: {svc.get('nameKo', entry.service_id)}** (`{entry.service_id}`)\n"
                f"  {entry.summary} ({ep_count}개 엔드포인트)\n"
            )
        elif entry.entry_type == "workflow":
            lines.append(
                f"- **워크플로우: {entry.summary}** (ID: `{entry.workflow_id}`)\n"
                f"  `get_workflow` 도구로 상세 조회 가능\n"
            )

    lines.append(
        "\n> 상세 정보는 `get_api_detail(service, endpoint_id)` 또는 "
        "`get_service_overview(service)`로 조회하세요."
    )
    return "\n".join(lines)
