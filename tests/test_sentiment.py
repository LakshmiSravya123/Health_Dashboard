"""Unit tests for sentiment analysis."""

import pytest
from src.models.sentiment.sentiment_analyzer import SentimentAnalyzer


@pytest.fixture
def analyzer():
    """Create sentiment analyzer instance."""
    return SentimentAnalyzer()


def test_analyze_positive_text(analyzer):
    """Test analysis of positive text."""
    text = "I feel great today! Everything is going well and I'm very happy."
    result = analyzer.analyze(text)
    
    assert result['sentiment_score'] > 0.5
    assert result['sentiment_label'] in ['positive', 'very_positive']
    assert result['confidence'] > 0


def test_analyze_negative_text(analyzer):
    """Test analysis of negative text."""
    text = "I'm feeling overwhelmed and stressed. Everything is too much."
    result = analyzer.analyze(text)
    
    assert result['sentiment_score'] < 0.5
    assert result['sentiment_label'] in ['negative', 'very_negative']
    assert 'stress' in result['keywords_detected'] or 'overwhelmed' in result['keywords_detected']


def test_analyze_empty_text(analyzer):
    """Test analysis of empty text."""
    result = analyzer.analyze("")
    
    assert result['sentiment_score'] == 0.5
    assert result['sentiment_label'] == 'neutral'
    assert result['confidence'] == 0.0


def test_analyze_batch(analyzer):
    """Test batch analysis."""
    texts = [
        "I'm happy and excited!",
        "Feeling sad and depressed",
        "Just a normal day"
    ]
    
    results = analyzer.analyze_batch(texts)
    
    assert len(results) == 3
    assert all('sentiment_score' in r for r in results)
    assert all('sentiment_label' in r for r in results)


def test_mental_health_indicators(analyzer):
    """Test mental health indicator detection."""
    text = "I'm experiencing severe anxiety and stress at work. Feeling burnt out."
    result = analyzer.analyze(text)
    
    indicators = result['mental_health_indicators']
    assert 'anxiety_score' in indicators
    assert 'stress_score' in indicators
    assert 'burnout_score' in indicators
    assert indicators['anxiety_score'] > 0


if __name__ == "__main__":
    pytest.main([__file__])
