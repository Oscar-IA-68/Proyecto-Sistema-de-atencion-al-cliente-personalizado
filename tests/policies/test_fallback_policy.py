"""
Tests para FAQFallbackPolicy.
"""

from src.policies.fallback_policy import FAQFallbackPolicy


class TestFAQFallbackPolicy:
    def test_should_use_faq_when_results_exist(self):
        policy = FAQFallbackPolicy()

        assert policy.should_use_faq([{"question": "q", "answer": "a"}]) is True

    def test_should_not_use_faq_when_results_empty(self):
        policy = FAQFallbackPolicy()

        assert policy.should_use_faq([]) is False

    def test_should_use_faq_when_multiple_results_exist(self):
        policy = FAQFallbackPolicy()

        assert policy.should_use_faq([
            {"question": "q1", "answer": "a1"},
            {"question": "q2", "answer": "a2"},
        ]) is True

    def test_should_not_use_faq_for_none_like_results(self):
        policy = FAQFallbackPolicy()

        assert policy.should_use_faq(None) is False
