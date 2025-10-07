"""Survey data extractor."""

from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import requests
from pathlib import Path
from src.etl.extractors.base_extractor import BaseExtractor
from src.utils.config_loader import get_config
from src.utils.logger import log


class SurveyExtractor(BaseExtractor):
    """Extract data from surveys and feedback forms."""
    
    def __init__(self):
        """Initialize survey extractor."""
        super().__init__('survey')
        
        config = get_config()
        self.survey_config = config.get('data_sources.surveys', {})
        self.employee_config = config.get('data_sources.employee_feedback', {})
    
    def extract(self, source_type: str = 'api', **kwargs) -> List[Dict[str, Any]]:
        """Extract survey data from various sources.
        
        Args:
            source_type: Type of source ('api', 'csv', 'database')
            **kwargs: Additional parameters for extraction
            
        Returns:
            List of extracted survey records
        """
        if source_type == 'api':
            return self._extract_from_api(**kwargs)
        elif source_type == 'csv':
            return self._extract_from_csv(**kwargs)
        else:
            log.warning(f"Unsupported source type: {source_type}")
            return []
    
    def _extract_from_api(
        self,
        endpoint: str = None,
        api_key: str = None,
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Extract survey data from API.
        
        Args:
            endpoint: API endpoint URL
            api_key: API key for authentication
            params: Query parameters
            
        Returns:
            List of extracted records
        """
        endpoint = endpoint or self.survey_config.get('api_endpoint')
        api_key = api_key or self.survey_config.get('api_key')
        
        if not endpoint or not api_key:
            log.warning("Survey API not configured")
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(endpoint, headers=headers, params=params or {})
            response.raise_for_status()
            
            data = response.json()
            records = []
            
            # Process survey responses (format may vary by provider)
            for item in data.get('responses', []):
                record = self._process_survey_response(item)
                if record:
                    records.append(record)
            
            log.info(f"Extracted {len(records)} survey responses from API")
            return records
        
        except requests.RequestException as e:
            log.error(f"Error extracting from survey API: {str(e)}")
            return []
    
    def _extract_from_csv(
        self,
        file_path: str = None,
        text_column: str = 'response_text',
        user_column: str = 'user_id',
        timestamp_column: str = 'timestamp'
    ) -> List[Dict[str, Any]]:
        """Extract survey data from CSV file.
        
        Args:
            file_path: Path to CSV file
            text_column: Name of column containing text responses
            user_column: Name of column containing user IDs
            timestamp_column: Name of column containing timestamps
            
        Returns:
            List of extracted records
        """
        file_path = file_path or self.employee_config.get('path')
        
        if not file_path:
            log.warning("CSV file path not configured")
            return []
        
        try:
            df = pd.read_csv(file_path)
            records = []
            
            for _, row in df.iterrows():
                # Parse timestamp
                try:
                    timestamp = pd.to_datetime(row[timestamp_column])
                except:
                    timestamp = datetime.utcnow()
                
                # Create record
                record = self.create_record(
                    user_id=str(row[user_column]),
                    text_content=str(row[text_column]),
                    timestamp=timestamp,
                    metadata={
                        'survey_type': row.get('survey_type', 'general'),
                        'additional_fields': {
                            k: v for k, v in row.items()
                            if k not in [text_column, user_column, timestamp_column]
                        }
                    }
                )
                records.append(record)
            
            log.info(f"Extracted {len(records)} survey responses from CSV")
            return records
        
        except Exception as e:
            log.error(f"Error extracting from CSV: {str(e)}")
            return []
    
    def _process_survey_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single survey response into standardized format.
        
        Args:
            response: Raw survey response data
            
        Returns:
            Standardized record or None if invalid
        """
        try:
            # Extract relevant fields (adjust based on your survey provider's format)
            user_id = response.get('respondent_id', response.get('user_id', 'anonymous'))
            
            # Combine all text responses
            text_parts = []
            for question, answer in response.get('answers', {}).items():
                if isinstance(answer, str) and answer.strip():
                    text_parts.append(f"{question}: {answer}")
            
            if not text_parts:
                return None
            
            text_content = "\n".join(text_parts)
            
            # Parse timestamp
            timestamp_str = response.get('submitted_at', response.get('timestamp'))
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.utcnow()
            
            return self.create_record(
                user_id=user_id,
                text_content=text_content,
                timestamp=timestamp,
                metadata={
                    'survey_id': response.get('survey_id'),
                    'response_id': response.get('response_id'),
                    'survey_name': response.get('survey_name'),
                    'completion_status': response.get('status', 'completed')
                }
            )
        
        except Exception as e:
            log.error(f"Error processing survey response: {str(e)}")
            return None
    
    def create_sample_data(self, output_path: str = None, num_records: int = 100) -> str:
        """Create sample survey data for testing.
        
        Args:
            output_path: Path to save sample CSV
            num_records: Number of sample records to create
            
        Returns:
            Path to created file
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "data" / "sample_survey_data.csv"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sample responses with varying sentiment
        sample_texts = [
            "I feel overwhelmed with work lately and struggling to maintain work-life balance",
            "The team support has been great, feeling motivated and energized",
            "Experiencing high levels of stress due to tight deadlines",
            "Really enjoying the new projects and feeling fulfilled",
            "Feeling burnt out and exhausted, need a break",
            "The flexible work schedule has improved my mental wellbeing significantly",
            "Anxiety about performance reviews is affecting my sleep",
            "Grateful for the mental health resources provided by the company",
            "Workload is manageable and I feel supported by my manager",
            "Feeling isolated working from home, missing team interactions"
        ]
        
        data = []
        for i in range(num_records):
            data.append({
                'user_id': f'user_{i % 50}',  # 50 unique users
                'response_text': sample_texts[i % len(sample_texts)],
                'timestamp': (datetime.utcnow() - pd.Timedelta(days=i % 30)).isoformat(),
                'survey_type': 'employee_wellbeing',
                'department': ['Engineering', 'Sales', 'Marketing', 'HR'][i % 4]
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        log.info(f"Created sample survey data at {output_path}")
        return str(output_path)
