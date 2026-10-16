from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents.viral_growth.growth_agent import (
    ComplianceGuardAgent,
    LocalOpsDashboardAgent,
    PerformanceAnalyticsAgent,
    ThumbnailEngineerAgent,
    TrendResearchAgent,
)


def test_trend_research_agent_builds_data():
    agent = TrendResearchAgent()
    topics = agent.build_daily_story_matrix(platform="youtube", max_topics=3)
    assert len(topics) == 3
    assert "expected_retention" not in topics[0]
    assert topics[0]["score_basis"] == "editorial_heuristic_not_live_trend_or_audience_data"


def test_thumbnail_and_dashboard_are_coherent():
    thumbnail = ThumbnailEngineerAgent().design_thumbnail("Funny Family Surprise", "Kaavya reacts", "youtube")
    dashboard = LocalOpsDashboardAgent().build_dashboard(
        batch=[{"id": "vid-1", "title": "Funny Family Surprise"}],
        quality_results=[{"id": "vid-1", "passed": True}],
        upload_results=[{"id": "vid-1", "status": "LIVE_POSTED"}],
    )
    compliance = ComplianceGuardAgent().check_content("Funny Family Surprise", "Kaavya reacts", "Follow and subscribe", "youtube")
    analytics = PerformanceAnalyticsAgent().evaluate_post({"average_watch_time": 15, "retention_rate": 78, "click_through_rate": 0.08, "likes_ratio": 2})

    assert "SURPRISE" in thumbnail["cta"]
    assert dashboard["overall_health"] == "green"
    assert compliance["safe"] is True
    assert analytics["recommendation"] in {"double_down_same_pattern", "keep_formula_and_test_variation"}


def test_performance_agent_refuses_to_score_missing_live_metrics():
    analytics = PerformanceAnalyticsAgent().evaluate_post({"views": 0})

    assert analytics["available"] is False
    assert analytics["score"] is None
    assert analytics["recommendation"] == "collect_analytics"
    assert "average_watch_time" in analytics["missing_metrics"]
