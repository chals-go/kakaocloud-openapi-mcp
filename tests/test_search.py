"""검색 유틸리티 및 데이터 로더 테스트."""

from kakaocloud_openapi_mcp.data.loader import get_store
from kakaocloud_openapi_mcp.utils.search import SearchEntry, search


def test_search_korean_keyword():
    """한국어 키워드로 검색이 동작하는지 확인한다."""
    store = get_store()
    results = search("VM 생성", store.search_index)
    assert len(results) > 0
    # BCS 서비스 또는 create-instance 엔드포인트가 포함되어야 함
    service_ids = {r.entry.service_id for r in results}
    assert "bcs" in service_ids


def test_search_english_keyword():
    """영어 키워드로 검색이 동작하는지 확인한다."""
    store = get_store()
    results = search("create instance", store.search_index)
    assert len(results) > 0


def test_search_empty_query():
    """빈 쿼리는 빈 결과를 반환한다."""
    store = get_store()
    results = search("", store.search_index)
    assert len(results) == 0


def test_search_no_results():
    """매칭 안 되는 쿼리는 빈 결과를 반환한다."""
    store = get_store()
    results = search("xyznonexistent", store.search_index)
    assert len(results) == 0


def test_search_workflow():
    """워크플로우 검색이 동작하는지 확인한다."""
    store = get_store()
    results = search("VM 만들기", store.search_index)
    workflow_results = [r for r in results if r.entry.entry_type == "workflow"]
    assert len(workflow_results) > 0


def test_service_alias_resolution():
    """서비스 별칭이 올바르게 해석되는지 확인한다."""
    store = get_store()
    assert store.resolve_service_id("vm") == "bcs"
    assert store.resolve_service_id("vpc") == "bns-vpc"
    assert store.resolve_service_id("lb") == "bns-load-balancer"
    assert store.resolve_service_id("k8s") == "container-pack"
    assert store.resolve_service_id("mysql") == "data-store-mysql"
    assert store.resolve_service_id("bcs") == "bcs"


def test_data_store_loaded():
    """모든 서비스 데이터가 로드되었는지 확인한다."""
    store = get_store()
    assert len(store.services) == 6
    assert len(store.workflows) == 5
    assert store.auth  # 인증 데이터 존재
    assert len(store.search_index) > 0


def test_get_endpoint():
    """엔드포인트 조회가 동작하는지 확인한다."""
    store = get_store()
    ep = store.get_endpoint("bcs", "create-instance")
    assert ep is not None
    assert ep["method"] == "POST"
    assert ep["path"] == "/instances"
