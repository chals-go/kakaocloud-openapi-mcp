"""get_workflow - 특정 작업의 전체 API 호출 흐름을 조회한다."""

from __future__ import annotations

from kakaocloud_openapi_mcp.data.loader import get_store
from kakaocloud_openapi_mcp.utils.search import SearchEntry, search


def get_workflow(task: str) -> str:
    """특정 작업(예: VM 생성, VPC 구성)의 전체 API 호출 흐름을 조회한다.

    Args:
        task: 작업 설명 (예: "VM 인스턴스 생성", "VPC 네트워크 구성")
    """
    store = get_store()

    # 워크플로우 검색 인덱스에서 매칭
    wf_entries = [e for e in store.search_index if e.entry_type == "workflow"]
    results = search(task, wf_entries, limit=3)

    if not results:
        # 사용 가능한 워크플로우 목록 반환
        if store.workflows:
            wf_list = "\n".join(
                f"- **{wf.get('nameKo', wf['name'])}** (ID: `{wf['id']}`)"
                for wf in store.workflows
            )
            return f"'{task}'에 해당하는 워크플로우를 찾을 수 없습니다.\n\n사용 가능한 워크플로우:\n{wf_list}"
        return f"'{task}'에 해당하는 워크플로우를 찾을 수 없습니다. 워크플로우 데이터가 아직 준비되지 않았습니다."

    # 가장 높은 점수의 워크플로우 반환
    best = results[0].entry
    wf = store.get_workflow(best.workflow_id) if best.workflow_id else None

    if not wf:
        return f"워크플로우 '{best.workflow_id}'의 데이터를 찾을 수 없습니다."

    lines: list[str] = []
    lines.append(f"# {wf.get('nameKo', wf['name'])}\n")
    lines.append(f"{wf.get('description', '')}\n")

    lines.append("## 단계별 API 호출 흐름\n")

    for step in wf.get("steps", []):
        lines.append(f"### Step {step['order']}: {step.get('actionKo', step['action'])}\n")
        lines.append(f"- **서비스:** `{step['service']}`")
        lines.append(f"- **API:** `{step['method']} {step['path']}`")
        if step.get("note"):
            lines.append(f"- **참고:** {step['note']}")
        if step.get("outputUsedBy"):
            lines.append(f"- **출력 사용처:** Step {', '.join(str(s) for s in step['outputUsedBy'])}")
        lines.append("")

    # 다른 관련 워크플로우 제안
    if len(results) > 1:
        lines.append("## 관련 워크플로우\n")
        for r in results[1:]:
            lines.append(f"- {r.entry.summary} (ID: `{r.entry.workflow_id}`)")

    return "\n".join(lines)
