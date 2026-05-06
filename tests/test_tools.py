"""MCP Tool 함수 테스트."""

from kakaocloud_openapi_mcp.tools.search import search_kakaocloud_api
from kakaocloud_openapi_mcp.tools.detail import get_api_detail
from kakaocloud_openapi_mcp.tools.overview import get_service_overview
from kakaocloud_openapi_mcp.tools.workflow import get_workflow
from kakaocloud_openapi_mcp.tools.auth import get_auth_guide


def test_search_tool():
    """search_kakaocloud_api 도구가 결과를 반환한다."""
    result = search_kakaocloud_api("VM 생성")
    assert "검색 결과" in result
    assert "bcs" in result


def test_search_tool_no_results():
    """검색 결과가 없으면 안내 메시지를 반환한다."""
    result = search_kakaocloud_api("xyznonexistent")
    assert "검색 결과가 없습니다" in result


def test_detail_tool():
    """get_api_detail 도구가 상세 정보를 반환한다."""
    result = get_api_detail("bcs", "create-instance")
    assert "VM 인스턴스 생성" in result
    assert "POST" in result
    assert "/instances" in result


def test_detail_tool_with_alias():
    """서비스 별칭으로 상세 조회가 동작한다."""
    result = get_api_detail("vm", "create-instance")
    assert "VM 인스턴스 생성" in result


def test_detail_tool_invalid_service():
    """존재하지 않는 서비스는 에러 메시지를 반환한다."""
    result = get_api_detail("nonexistent", "create-instance")
    assert "찾을 수 없습니다" in result


def test_detail_tool_invalid_endpoint():
    """존재하지 않는 엔드포인트는 에러 메시지를 반환한다."""
    result = get_api_detail("bcs", "nonexistent")
    assert "찾을 수 없습니다" in result


def test_overview_tool():
    """get_service_overview 도구가 서비스 개요를 반환한다."""
    result = get_service_overview("bcs")
    assert "비욘드 컴퓨트 서비스" in result
    assert "엔드포인트" in result


def test_overview_tool_with_alias():
    """서비스 별칭으로 개요 조회가 동작한다."""
    result = get_service_overview("mysql")
    assert "데이터 스토어" in result


def test_overview_tool_invalid():
    """존재하지 않는 서비스는 에러 메시지를 반환한다."""
    result = get_service_overview("nonexistent")
    assert "찾을 수 없습니다" in result


def test_workflow_tool():
    """get_workflow 도구가 워크플로우를 반환한다."""
    result = get_workflow("VM 인스턴스 생성")
    assert "Step" in result
    assert "인증 토큰" in result


def test_workflow_tool_no_match():
    """매칭 안 되는 워크플로우는 목록을 안내한다."""
    result = get_workflow("xyznonexistent")
    assert "찾을 수 없습니다" in result


def test_auth_tool():
    """get_auth_guide 도구가 인증 가이드를 반환한다."""
    result = get_auth_guide()
    assert "인증" in result
    assert "X-Auth-Token" in result
    assert "python" in result.lower() or "Python" in result


def test_auth_tool_includes_cloudtrail():
    """get_auth_guide 출력에 CloudTrail 감사 로그 안내가 포함된다."""
    result = get_auth_guide()
    assert "CloudTrail" in result
    assert "감사 로그" in result


def test_detail_tool_operate_instance():
    """통합 액션 엔드포인트(operate-instance) 상세에 6개 액션이 모두 명시된다."""
    result = get_api_detail("bcs", "operate-instance")
    assert "/instances/:instance_id/actions" in result
    assert "action" in result
    for action in ("start", "stop", "shelve", "unshelve", "soft-reboot", "hard-reboot"):
        assert action in result


def test_detail_tool_lb_create_extended():
    """로드밸런서 생성 상세에 target_groups, listeners 필드가 포함된다."""
    result = get_api_detail("bns-load-balancer", "create-load-balancer")
    assert "target_groups" in result
    assert "listeners" in result


def test_search_finds_operate_instance():
    """'인스턴스 상태 변경' 검색 시 operate-instance가 결과에 포함된다."""
    result = search_kakaocloud_api("인스턴스 상태 변경")
    assert "operate-instance" in result
