"""카카오클라우드 API 스펙 JSON 데이터를 로드하고 검색 인덱스를 구축한다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kakaocloud_openapi_mcp.utils.search import SearchEntry

DATA_DIR = Path(__file__).parent
SERVICES_DIR = DATA_DIR / "services"

# 서비스 별칭 → 실제 서비스 ID 매핑
SERVICE_ALIASES: dict[str, str] = {
    "vm": "bcs",
    "virtual-machine": "bcs",
    "compute": "bcs",
    "인스턴스": "bcs",
    "가상머신": "bcs",
    "서버": "bcs",
    "instance": "bcs",
    "vpc": "bns-vpc",
    "네트워크": "bns-vpc",
    "서브넷": "bns-vpc",
    "subnet": "bns-vpc",
    "security-group": "bns-vpc",
    "보안그룹": "bns-vpc",
    "load-balancer": "bns-load-balancer",
    "lb": "bns-load-balancer",
    "로드밸런서": "bns-load-balancer",
    "transit-gateway": "bns-transit-gateway",
    "tgw": "bns-transit-gateway",
    "kubernetes": "container-pack",
    "k8s": "container-pack",
    "컨테이너": "container-pack",
    "mysql": "data-store-mysql",
    "database": "data-store-mysql",
    "db": "data-store-mysql",
    "데이터베이스": "data-store-mysql",
}


class DataStore:
    """모든 API 스펙 데이터를 메모리에 보관하고 검색 인덱스를 제공한다."""

    def __init__(self) -> None:
        self.services: dict[str, dict[str, Any]] = {}
        self.workflows: list[dict[str, Any]] = []
        self.auth: dict[str, Any] = {}
        self.search_index: list[SearchEntry] = []
        self._load()

    def _load(self) -> None:
        # 서비스 JSON 로드
        if SERVICES_DIR.exists():
            for path in sorted(SERVICES_DIR.glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.services[data["id"]] = data

        # 워크플로우 로드
        workflows_path = DATA_DIR / "workflows.json"
        if workflows_path.exists():
            self.workflows = json.loads(
                workflows_path.read_text(encoding="utf-8")
            ).get("workflows", [])

        # 인증 가이드 로드
        auth_path = DATA_DIR / "auth.json"
        if auth_path.exists():
            self.auth = json.loads(auth_path.read_text(encoding="utf-8"))

        # 검색 인덱스 구축
        self._build_index()

    def _build_index(self) -> None:
        index: list[SearchEntry] = []

        for svc in self.services.values():
            # 서비스 레벨 엔트리
            index.append(
                SearchEntry(
                    service_id=svc["id"],
                    endpoint_id=None,
                    entry_type="service",
                    keywords=svc.get("keywords", []) + [svc["id"], svc.get("name", ""), svc.get("nameKo", "")],
                    summary=svc.get("description", svc.get("name", "")),
                )
            )

            # 엔드포인트 레벨 엔트리
            for ep in svc.get("endpoints", []):
                index.append(
                    SearchEntry(
                        service_id=svc["id"],
                        endpoint_id=ep["id"],
                        entry_type="endpoint",
                        keywords=ep.get("keywords", []) + [ep.get("summary", ""), ep.get("summaryKo", "")],
                        summary=ep.get("summary", ""),
                        method=ep.get("method"),
                        path=ep.get("path"),
                    )
                )

        # 워크플로우 엔트리
        for wf in self.workflows:
            index.append(
                SearchEntry(
                    service_id="",
                    endpoint_id=None,
                    entry_type="workflow",
                    keywords=wf.get("keywords", []) + [wf.get("name", ""), wf.get("nameKo", "")],
                    summary=wf.get("name", ""),
                    workflow_id=wf.get("id"),
                )
            )

        self.search_index = index

    def resolve_service_id(self, name: str) -> str | None:
        """서비스 이름 또는 별칭을 실제 서비스 ID로 변환한다."""
        lower = name.lower().strip()
        if lower in self.services:
            return lower
        if lower in SERVICE_ALIASES:
            return SERVICE_ALIASES[lower]
        # 부분 매칭 시도
        for sid in self.services:
            if lower in sid or sid in lower:
                return sid
        return None

    def get_service(self, name: str) -> dict[str, Any] | None:
        sid = self.resolve_service_id(name)
        if sid and sid in self.services:
            return self.services[sid]
        return None

    def get_endpoint(self, service_name: str, endpoint_id: str) -> dict[str, Any] | None:
        svc = self.get_service(service_name)
        if not svc:
            return None
        for ep in svc.get("endpoints", []):
            if ep["id"] == endpoint_id:
                return ep
        return None

    def get_workflow(self, workflow_id: str) -> dict[str, Any] | None:
        for wf in self.workflows:
            if wf["id"] == workflow_id:
                return wf
        return None


# 싱글턴 인스턴스
_store: DataStore | None = None


def get_store() -> DataStore:
    global _store
    if _store is None:
        _store = DataStore()
    return _store
