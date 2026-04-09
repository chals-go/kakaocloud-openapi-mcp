"""카카오클라우드 OpenAPI MCP 서버 진입점."""

from mcp.server.fastmcp import FastMCP

from kakaocloud_openapi_mcp.tools.search import search_kakaocloud_api
from kakaocloud_openapi_mcp.tools.detail import get_api_detail
from kakaocloud_openapi_mcp.tools.overview import get_service_overview
from kakaocloud_openapi_mcp.tools.workflow import get_workflow
from kakaocloud_openapi_mcp.tools.auth import get_auth_guide
from kakaocloud_openapi_mcp.resources.services import (
    get_auth_resource,
    get_service_detail,
    get_services_list,
)

mcp = FastMCP(
    "kakaocloud-openapi",
    instructions=(
        "카카오클라우드 OpenAPI 문서를 제공하는 MCP 서버입니다. "
        "카카오클라우드의 VM, VPC, Load Balancer, Kubernetes, MySQL 등의 "
        "API 사용법을 검색하고 조회할 수 있습니다. "
        "API를 직접 호출하지 않고 API 문서 정보를 제공합니다."
    ),
)

# --- Tools ---

mcp.tool()(search_kakaocloud_api)
mcp.tool()(get_api_detail)
mcp.tool()(get_service_overview)
mcp.tool()(get_workflow)
mcp.tool()(get_auth_guide)


# --- Resources ---


@mcp.resource("kakaocloud://services")
def services_resource() -> str:
    """카카오클라우드 전체 서비스 목록"""
    return get_services_list()


@mcp.resource("kakaocloud://service/{name}")
def service_resource(name: str) -> str:
    """특정 카카오클라우드 서비스의 전체 API 스펙"""
    return get_service_detail(name)


@mcp.resource("kakaocloud://auth")
def auth_resource() -> str:
    """카카오클라우드 API 인증 가이드"""
    return get_auth_resource()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
