"""Burnout prediction model."""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
from src.utils.config_loader import get_config
from src.utils.logger import log


class BurnoutPredictor:
    """Predict burnout risk using machine learning."""
    
    def __init__(self, model_path: str = None):
        """Initialize burnout predictor.
        
        Args:
            model_path: Path to saved model (if None, creates new model)
        """
        self.config = get_config()
        burnout_config = self.config.get_burnout_config()
        
        self.model_type = burnout_config.get('model_type', 'ensemble')
        self.feature_names = burnout_config.get('features', [])
        self.risk_levels = burnout_config.get('risk_levels', {})
        
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self._init_model()
    
    def _init_model(self):
        """Initialize the prediction model."""
        if self.model_type == 'xgboost':
            try:
                from xgboost import XGBClassifier
                self.model = XGBClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
            except ImportError:
                log.warning("XGBoost not available, using GradientBoosting instead")
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
        elif self.model_type == 'ensemble':
            # Use RandomForest as default ensemble
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        log.info(f"Initialized {self.model_type} model")
    
    def train(
        self,
        features_df: pd.DataFrame,
        labels: np.ndarray = None,
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """Train the burnout prediction model.
        
        Args:
            features_df: DataFrame with user features
            labels: Ground truth labels (if None, uses synthetic labels)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        X = self._prepare_features(features_df)
        
        # Generate or use provided labels
        if labels is None:
            log.warning("No labels provided, generating synthetic labels for demonstration")
            y = self._generate_synthetic_labels(features_df)
        else:
            y = labels
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        log.info("Training burnout prediction model...")
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        metrics = {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
        
        log.info(f"Model trained - Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
        
        return metrics
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict burnout risk for a single user.
        
        Args:
            features: Dictionary of user features
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load a trained model.")
        
        # Prepare features
        feature_vector = self._extract_feature_vector(features)
        X = np.array([feature_vector])
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_score = self.model.predict_proba(X_scaled)[0][1]  # Probability of high risk
        risk_level = self._get_risk_level(risk_score)
        
        # Get feature importance
        contributing_factors = self._get_contributing_factors(feature_vector)
        
        return {
            'prediction_id': self._generate_prediction_id(features),
            'user_id_hash': features.get('user_id_hash'),
            'prediction_date': features.get('feature_date'),
            'prediction_timestamp': datetime.utcnow().isoformat(),
            'burnout_risk_score': round(risk_score, 3),
            'risk_level': risk_level,
            'confidence_interval': {
                'lower_bound': max(0, risk_score - 0.1),
                'upper_bound': min(1, risk_score + 0.1)
            },
            'contributing_factors': contributing_factors,
            'prediction_horizon_days': 7,
            'model_version': f'{self.model_type}_v1.0',
            'model_type': self.model_type
        }
    
    def predict_batch(self, features_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict burnout risk for multiple users.
        
        Args:
            features_df: DataFrame with user features
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load a trained model.")
        
        # Prepare features
        X = self._prepare_features(features_df)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        proba = self.model.predict_proba(X_scaled)
        # Handle both binary and multi-class cases
        if proba.shape[1] == 1:
            # Only one class predicted, use those probabilities
            risk_scores = proba[:, 0]
        else:
            # Binary classification, use positive class probability
            risk_scores = proba[:, 1]
        
        # Create predictions
        predictions = []
        for idx, (_, row) in enumerate(features_df.iterrows()):
            risk_score = risk_scores[idx]
            risk_level = self._get_risk_level(risk_score)
            
            feature_vector = X[idx]
            contributing_factors = self._get_contributing_factors(feature_vector)
            
            predictions.append({
                'prediction_id': self._generate_prediction_id(row.to_dict()),
                'user_id_hash': row.get('user_id_hash'),
                'prediction_date': row.get('feature_date'),
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'burnout_risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'confidence_interval': {
                    'lower_bound': max(0, risk_score - 0.1),
                    'upper_bound': min(1, risk_score + 0.1)
                },
                'contributing_factors': contributing_factors,
                'prediction_horizon_days': 7,
                'model_version': f'{self.model_type}_v1.0',
                'model_type': self.model_type
            })
        
        return predictions
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare feature matrix from DataFrame.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Feature matrix
        """
        # Select feature columns
        feature_cols = [col for col in self.feature_names if col in df.columns]
        
        if not feature_cols:
            # Use all numeric columns except identifiers
            feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in feature_cols if col not in ['user_id_hash', 'feature_date']]
        
        # Fill missing values
        X = df[feature_cols].fillna(0).values
        
        return X
    
    def _extract_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Extract feature vector from feature dictionary.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Feature vector
        """
        vector = []
        for feature_name in self.feature_names:
            value = features.get(feature_name, 0)
            vector.append(value if value is not None else 0)
        
        return np.array(vector)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level.
        
        Args:
            risk_score: Risk score (0-1)
            
        Returns:
            Risk level string
        """
        if risk_score >= self.risk_levels.get('critical', 0.9):
            return 'critical'
        elif risk_score >= self.risk_levels.get('high', 0.8):
            return 'high'
        elif risk_score >= self.risk_levels.get('medium', 0.6):
            return 'medium'
        else:
            return 'low'
    
    def _get_contributing_factors(self, feature_vector: np.ndarray) -> List[Dict[str, Any]]:
        """Get top contributing factors for prediction.
        
        Args:
            feature_vector: Feature vector
            
        Returns:
            List of contributing factors with importance scores
        """
        if not hasattr(self.model, 'feature_importances_'):
            return []
        
        importances = self.model.feature_importances_
        
        # Get top 5 features
        top_indices = np.argsort(importances)[-5:][::-1]
        
        factors = []
        for idx in top_indices:
            if idx < len(self.feature_names):
                factors.append({
                    'factor_name': self.feature_names[idx],
                    'importance_score': round(float(importances[idx]), 3)
                })
        
        return factors
    
    def _generate_synthetic_labels(self, features_df: pd.DataFrame) -> np.ndarray:
        """Generate synthetic labels for demonstration purposes.
        
        Args:
            features_df: DataFrame with features
            
        Returns:
            Array of labels (0=low risk, 1=high risk)
        """
        # Simple heuristic: high risk if multiple negative indicators
        labels = []
        
        for _, row in features_df.iterrows():
            risk_score = 0
            
            # Low sentiment
            if row.get('avg_sentiment_7d', 0.5) < 0.3:
                risk_score += 1
            
            # High volatility
            if row.get('sentiment_volatility', 0) > 0.3:
                risk_score += 1
            
            # Many negative posts
            if row.get('negative_post_count_7d', 0) > 5:
                risk_score += 1
            
            # High burnout indicators
            if row.get('burnout_indicator_avg', 0) > 0.5:
                risk_score += 1
            
            # Negative trend
            if row.get('sentiment_trend_7d', 0) < -0.1:
                risk_score += 1
            
            # High risk if 3 or more indicators
            labels.append(1 if risk_score >= 3 else 0)
        
        return np.array(labels)
    
    def _generate_prediction_id(self, features: Dict[str, Any]) -> str:
        """Generate unique prediction ID.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Prediction ID
        """
        import hashlib
        user_id = features.get('user_id_hash', 'unknown')
        date = features.get('feature_date', datetime.utcnow().date().isoformat())
        combined = f"{user_id}_{date}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def save_model(self, path: str):
        """Save trained model to disk.
        
        Args:
            path: Path to save model
        """
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'risk_levels': self.risk_levels
        }
        
        joblib.dump(model_data, path)
        log.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk.
        
        Args:
            path: Path to saved model
        """
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.risk_levels = model_data['risk_levels']
        self.is_trained = True
        
        log.info(f"Model loaded from {path}")
