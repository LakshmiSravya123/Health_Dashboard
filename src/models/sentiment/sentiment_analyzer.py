"""Sentiment analysis module using transformers."""

from typing import List, Dict, Any, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import numpy as np
from datetime import datetime
from src.utils.config_loader import get_config
from src.utils.logger import log


class SentimentAnalyzer:
    """Analyze sentiment using transformer models."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.config = get_config()
        sentiment_config = self.config.get_sentiment_config()
        
        self.model_type = sentiment_config.get('model_type', 'transformer')
        self.model_name = sentiment_config.get('transformer_model', 'distilbert-base-uncased-finetuned-sst-2-english')
        self.batch_size = sentiment_config.get('batch_size', 32)
        self.max_length = sentiment_config.get('max_length', 512)
        self.thresholds = sentiment_config.get('thresholds', {})
        self.keywords = sentiment_config.get('mental_health_keywords', {})
        
        # Initialize model
        self._init_model()
        
        log.info(f"Sentiment analyzer initialized with model: {self.model_name}")
    
    def _init_model(self):
        """Initialize the sentiment analysis model."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=device,
                truncation=True,
                max_length=self.max_length
            )
            
            log.info(f"Model loaded on device: {'GPU' if device == 0 else 'CPU'}")
        
        except Exception as e:
            log.error(f"Error loading model: {str(e)}")
            raise
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or not text.strip():
            return self._empty_result()
        
        try:
            # Get sentiment from model
            result = self.sentiment_pipeline(text[:self.max_length])[0]
            
            # Convert to 0-1 score (negative to positive)
            sentiment_score = self._convert_to_score(result)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # Detect mental health indicators
            indicators = self._detect_mental_health_indicators(text)
            keywords_detected = self._extract_keywords(text)
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': result['score'],
                'mental_health_indicators': indicators,
                'keywords_detected': keywords_detected,
                'model_version': self.model_name,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            log.error(f"Error analyzing text: {str(e)}")
            return self._empty_result()
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts in batch.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        if not texts:
            return []
        
        results = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Get sentiment predictions
                predictions = self.sentiment_pipeline(
                    [text[:self.max_length] for text in batch]
                )
                
                # Process each result
                for text, pred in zip(batch, predictions):
                    sentiment_score = self._convert_to_score(pred)
                    sentiment_label = self._get_sentiment_label(sentiment_score)
                    indicators = self._detect_mental_health_indicators(text)
                    keywords = self._extract_keywords(text)
                    
                    results.append({
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'confidence': pred['score'],
                        'mental_health_indicators': indicators,
                        'keywords_detected': keywords,
                        'model_version': self.model_name,
                        'processing_timestamp': datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                log.error(f"Error processing batch: {str(e)}")
                # Add empty results for failed batch
                results.extend([self._empty_result() for _ in batch])
        
        return results
    
    def _convert_to_score(self, result: Dict[str, Any]) -> float:
        """Convert model output to 0-1 sentiment score.
        
        Args:
            result: Model prediction result
            
        Returns:
            Sentiment score (0=very negative, 1=very positive)
        """
        label = result['label'].upper()
        score = result['score']
        
        if 'POSITIVE' in label:
            # Positive: map to 0.5-1.0
            return 0.5 + (score * 0.5)
        else:
            # Negative: map to 0.0-0.5
            return 0.5 - (score * 0.5)
    
    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score.
        
        Args:
            score: Sentiment score (0-1)
            
        Returns:
            Sentiment label
        """
        if score < self.thresholds.get('very_negative', 0.2):
            return 'very_negative'
        elif score < self.thresholds.get('negative', 0.4):
            return 'negative'
        elif score < self.thresholds.get('neutral', 0.6):
            return 'neutral'
        elif score < self.thresholds.get('positive', 0.8):
            return 'positive'
        else:
            return 'very_positive'
    
    def _detect_mental_health_indicators(self, text: str) -> Dict[str, float]:
        """Detect mental health indicators in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of indicator scores
        """
        text_lower = text.lower()
        indicators = {}
        
        for indicator_type, keywords in self.keywords.items():
            # Count keyword occurrences
            count = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by text length and number of keywords
            score = min(count / max(len(keywords) * 0.1, 1), 1.0)
            indicators[f'{indicator_type}_score'] = round(score, 3)
        
        return indicators
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract mental health keywords from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected keywords
        """
        text_lower = text.lower()
        detected = []
        
        for indicator_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text_lower and keyword not in detected:
                    detected.append(keyword)
        
        return detected
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result for failed analysis.
        
        Returns:
            Empty result dictionary
        """
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'mental_health_indicators': {},
            'keywords_detected': [],
            'model_version': self.model_name,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
    
    def process_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sentiment for a list of records.
        
        Args:
            records: List of records with 'text_content' field
            
        Returns:
            List of processed records with sentiment analysis
        """
        if not records:
            return []
        
        # Extract texts
        texts = [record.get('text_content', '') for record in records]
        
        # Analyze in batch
        sentiment_results = self.analyze_batch(texts)
        
        # Combine with original records
        processed = []
        for record, sentiment in zip(records, sentiment_results):
            processed_record = {
                'record_id': record.get('record_id'),
                'user_id_hash': record.get('user_id_hash'),
                'timestamp': record.get('timestamp'),
                **sentiment
            }
            processed.append(processed_record)
        
        return processed
