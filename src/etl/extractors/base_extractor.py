"""Base extractor class for data extraction."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import hashlib
from src.utils.logger import log


class BaseExtractor(ABC):
    """Abstract base class for data extractors."""
    
    def __init__(self, source_name: str):
        """Initialize base extractor.
        
        Args:
            source_name: Name of the data source
        """
        self.source_name = source_name
        self.extraction_timestamp = None
    
    @abstractmethod
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract data from source.
        
        Returns:
            List of extracted records
        """
        pass
    
    def anonymize_user_id(self, user_id: str, salt: str = "") -> str:
        """Anonymize user ID using SHA-256 hashing.
        
        Args:
            user_id: Original user ID
            salt: Salt for hashing
            
        Returns:
            Anonymized user ID hash
        """
        combined = f"{user_id}{salt}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    
    def create_record(
        self,
        user_id: str,
        text_content: str,
        timestamp: datetime,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create standardized record for loading.
        
        Args:
            user_id: User identifier
            text_content: Text content
            timestamp: Content timestamp
            metadata: Additional metadata
            
        Returns:
            Standardized record dictionary
        """
        record_id = hashlib.sha256(
            f"{user_id}{timestamp.isoformat()}{text_content[:50]}".encode('utf-8')
        ).hexdigest()
        
        return {
            'record_id': record_id,
            'user_id_hash': self.anonymize_user_id(user_id),
            'source': self.source_name,
            'text_content': text_content,
            'timestamp': timestamp.isoformat(),
            'metadata': metadata or {},
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'language': self._detect_language(text_content)
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text (simplified version).
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (default: 'en')
        """
        # Simplified - in production, use langdetect or similar
        return 'en'
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate record has required fields.
        
        Args:
            record: Record to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['record_id', 'user_id_hash', 'source', 'timestamp']
        
        for field in required_fields:
            if field not in record or record[field] is None:
                log.warning(f"Invalid record: missing {field}")
                return False
        
        return True
    
    def extract_with_validation(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract data with validation.
        
        Returns:
            List of validated records
        """
        self.extraction_timestamp = datetime.utcnow()
        log.info(f"Starting extraction from {self.source_name}")
        
        try:
            records = self.extract(**kwargs)
            valid_records = [r for r in records if self.validate_record(r)]
            
            log.info(
                f"Extracted {len(valid_records)} valid records from {self.source_name} "
                f"({len(records) - len(valid_records)} invalid)"
            )
            
            return valid_records
        
        except Exception as e:
            log.error(f"Error extracting from {self.source_name}: {str(e)}")
            raise
