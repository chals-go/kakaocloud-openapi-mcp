"""MCP Resource 핸들러 — 카카오클라우드 API 스펙 데이터를 Resource로 제공한다."""

from __future__ import annotations

import json

from kakaocloud_openapi_mcp.data.loader import get_store


def get_services_list() -> str:
    """전체 서비스 목록을 반환한다."""
    store = get_store()
    services = []
    for svc in store.services.values():
        services.append({
            "id": svc["id"],
            "name": svc.get("name", ""),
            "nameKo": svc.get("nameKo", ""),
            "description": svc.get("description", ""),
            "endpointCount": len(svc.get("endpoints", [])),
        })
    return json.dumps(services, indent=2, ensure_ascii=False)


def get_service_detail(name: str) -> str:
    """특정 서비스의 전체 API 스펙을 반환한다."""
    store = get_store()
    svc = store.get_service(name)
    if not svc:
        return json.dumps({"error": f"Service '{name}' not found"})
    return json.dumps(svc, indent=2, ensure_ascii=False)


def get_auth_resource() -> str:
    """인증 가이드 데이터를 반환한다."""
    store = get_store()
    return json.dumps(store.auth, indent=2, ensure_ascii=False)
