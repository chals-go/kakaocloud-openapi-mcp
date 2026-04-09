"""키워드 기반 검색 유틸리티. 한국어/영어 모두 지원."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchEntry:
    service_id: str
    endpoint_id: str | None
    entry_type: str  # "service", "endpoint", "workflow"
    keywords: list[str]
    summary: str
    method: str | None = None
    path: str | None = None
    workflow_id: str | None = None


@dataclass
class SearchResult:
    score: float
    entry: SearchEntry


def _tokenize(text: str) -> list[str]:
    """쿼리를 소문자 토큰으로 분리한다."""
    return text.lower().split()


def search(query: str, index: list[SearchEntry], limit: int = 10) -> list[SearchResult]:
    """키워드 기반 검색. 부분 문자열 매칭을 지원하여 한국어에 대응한다."""
    tokens = _tokenize(query)
    if not tokens:
        return []

    results: list[SearchResult] = []

    for entry in index:
        score = 0.0
        keywords_lower = " ".join(entry.keywords).lower()
        summary_lower = entry.summary.lower()
        searchable = keywords_lower + " " + summary_lower

        for token in tokens:
            if token in searchable:
                # 정확한 키워드 매칭은 높은 점수
                if any(token == kw.lower() for kw in entry.keywords):
                    score += 2.0
                # 부분 문자열 매칭
                else:
                    score += 1.0

        if score > 0:
            results.append(SearchResult(score=score, entry=entry))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
