from src.legal_matter_cost import review_decision


def test_near_deadline_high_usage_is_sent_to_human_review() -> None:
    assert review_decision(follow_up_days=5, total_tokens=900) is True
    assert review_decision(follow_up_days=8, total_tokens=1200) is False
    assert review_decision(follow_up_days=5, total_tokens=899) is False
