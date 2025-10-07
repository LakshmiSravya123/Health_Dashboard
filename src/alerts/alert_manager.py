"""Alert management system for burnout risks."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from src.etl.loaders.bigquery_loader import BigQueryLoader
from src.utils.config_loader import get_config
from src.utils.logger import log


class AlertManager:
    """Manage alerts for burnout risks."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.config = get_config()
        self.loader = BigQueryLoader()
        
        self.alert_config = self.config.get_alert_config()
        self.enabled = self.alert_config.get('enabled', True)
        self.channels = self.alert_config.get('channels', {})
        self.rules = self.alert_config.get('rules', [])
    
    def check_and_send_alerts(self) -> int:
        """Check for alert conditions and send alerts.
        
        Returns:
            Number of alerts sent
        """
        if not self.enabled:
            log.info("Alerts are disabled")
            return 0
        
        log.info("Checking for alert conditions...")
        
        # Get latest predictions
        predictions = self._get_latest_predictions()
        
        if predictions.empty:
            log.info("No predictions available for alerting")
            return 0
        
        alerts_sent = 0
        
        for _, prediction in predictions.iterrows():
            # Check each rule
            for rule in self.rules:
                if self._check_rule(prediction, rule):
                    # Check cooldown
                    if self._check_cooldown(prediction['user_id_hash'], rule['name']):
                        self._send_alert(prediction, rule)
                        alerts_sent += 1
        
        log.info(f"Sent {alerts_sent} alerts")
        return alerts_sent
    
    def _get_latest_predictions(self) -> pd.DataFrame:
        """Get latest predictions from BigQuery.
        
        Returns:
            DataFrame of predictions
        """
        tables = self.loader.tables
        predictions_table = tables.get('burnout_predictions', 'burnout_predictions')
        
        sql = f"""
        SELECT *
        FROM `{self.loader.project_id}.{self.loader.dataset_id}.{predictions_table}`
        WHERE prediction_date = CURRENT_DATE()
        """
        
        return self.loader.query(sql)
    
    def _check_rule(self, prediction: pd.Series, rule: Dict[str, Any]) -> bool:
        """Check if prediction meets alert rule condition.
        
        Args:
            prediction: Prediction record
            rule: Alert rule
            
        Returns:
            True if condition is met
        """
        condition = rule.get('condition', '')
        
        try:
            # Simple condition evaluation
            if 'burnout_risk' in condition:
                burnout_risk = prediction.get('burnout_risk_score', 0)
                return eval(condition.replace('burnout_risk', str(burnout_risk)))
            elif 'avg_sentiment' in condition:
                # Would need to fetch sentiment data
                return False
            elif 'sentiment_change' in condition:
                # Would need to calculate change
                return False
        except Exception as e:
            log.error(f"Error evaluating rule condition: {str(e)}")
            return False
        
        return False
    
    def _check_cooldown(self, user_id_hash: str, rule_name: str) -> bool:
        """Check if alert is in cooldown period.
        
        Args:
            user_id_hash: User ID
            rule_name: Name of alert rule
            
        Returns:
            True if not in cooldown
        """
        tables = self.loader.tables
        alerts_table = tables.get('alerts', 'alert_history')
        
        # Get rule cooldown
        rule = next((r for r in self.rules if r['name'] == rule_name), None)
        if not rule:
            return True
        
        cooldown_hours = rule.get('cooldown_hours', 24)
        
        sql = f"""
        SELECT MAX(alert_timestamp) as last_alert
        FROM `{self.loader.project_id}.{self.loader.dataset_id}.{alerts_table}`
        WHERE user_id_hash = '{user_id_hash}'
            AND alert_type = '{rule_name}'
            AND alert_timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {cooldown_hours} HOUR)
        """
        
        try:
            result = self.loader.query(sql)
            return result.empty or pd.isna(result.iloc[0]['last_alert'])
        except:
            return True
    
    def _send_alert(self, prediction: pd.Series, rule: Dict[str, Any]):
        """Send alert through configured channels.
        
        Args:
            prediction: Prediction record
            rule: Alert rule that triggered
        """
        alert_data = {
            'alert_id': self._generate_alert_id(),
            'user_id_hash': prediction.get('user_id_hash'),
            'alert_timestamp': datetime.utcnow().isoformat(),
            'alert_type': rule['name'],
            'severity': rule.get('severity', 'medium'),
            'trigger_condition': rule.get('condition'),
            'trigger_value': prediction.get('burnout_risk_score'),
            'channels_sent': [],
            'status': 'sent',
            'acknowledged_timestamp': None,
            'acknowledged_by': None,
            'notes': None
        }
        
        # Send through email
        if self.channels.get('email', {}).get('enabled', False):
            try:
                self._send_email_alert(prediction, rule)
                alert_data['channels_sent'].append('email')
            except Exception as e:
                log.error(f"Error sending email alert: {str(e)}")
                alert_data['status'] = 'failed'
        
        # Send through Slack
        if self.channels.get('slack', {}).get('enabled', False):
            try:
                self._send_slack_alert(prediction, rule)
                alert_data['channels_sent'].append('slack')
            except Exception as e:
                log.error(f"Error sending Slack alert: {str(e)}")
        
        # Log alert to BigQuery
        self.loader.load_alert_history([alert_data])
        
        log.info(f"Alert sent for user {prediction.get('user_id_hash')}: {rule['name']}")
    
    def _send_email_alert(self, prediction: pd.Series, rule: Dict[str, Any]):
        """Send email alert.
        
        Args:
            prediction: Prediction record
            rule: Alert rule
        """
        email_config = self.channels.get('email', {})
        
        sender_email = email_config.get('sender_email')
        sender_password = email_config.get('sender_password')
        smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = email_config.get('smtp_port', 587)
        
        if not sender_email or not sender_password:
            log.warning("Email credentials not configured")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # In production, send to appropriate recipient
        msg['Subject'] = f"Mental Health Alert: {rule['name']}"
        
        body = f"""
        Mental Health Alert
        
        Alert Type: {rule['name']}
        Severity: {rule.get('severity', 'medium').upper()}
        
        User ID: {prediction.get('user_id_hash')}
        Burnout Risk Score: {prediction.get('burnout_risk_score', 0):.2f}
        Risk Level: {prediction.get('risk_level', 'unknown').upper()}
        
        This alert was triggered based on the following condition:
        {rule.get('condition')}
        
        Please review the dashboard for more details and consider reaching out to provide support.
        
        ---
        Mental Health Dashboard
        Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    
    def _send_slack_alert(self, prediction: pd.Series, rule: Dict[str, Any]):
        """Send Slack alert.
        
        Args:
            prediction: Prediction record
            rule: Alert rule
        """
        import requests
        
        slack_config = self.channels.get('slack', {})
        webhook_url = slack_config.get('webhook_url')
        
        if not webhook_url:
            log.warning("Slack webhook not configured")
            return
        
        message = {
            "text": f"*Mental Health Alert: {rule['name']}*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {rule['name']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{rule.get('severity', 'medium').upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Risk Score:*\n{prediction.get('burnout_risk_score', 0):.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Risk Level:*\n{prediction.get('risk_level', 'unknown').upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*User ID:*\n{prediction.get('user_id_hash')[:16]}..."
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID.
        
        Returns:
            Alert ID
        """
        import hashlib
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]


def main():
    """Main function to check and send alerts."""
    manager = AlertManager()
    count = manager.check_and_send_alerts()
    log.info(f"Alert processing complete. Alerts sent: {count}")


if __name__ == "__main__":
    main()
