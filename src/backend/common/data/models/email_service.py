from dataclasses import dataclass
from typing import Optional

@dataclass
class SMTPConfig:
    """SMTP email service configuration."""
    hostname: str
    port: int


@dataclass
class SESConfig:
    """Amazon SES email service configuration."""
    access_key_id: str
    secret_access_key: str
    region: str


@dataclass
class EmailServiceConfig:
    """Configuration settings for email service (SMTP or SES)."""
    # Common settings
    from_email: str
    site_url: str
    use_ses: bool = False
    
    # Service-specific configs - only one will be used based on use_ses
    smtp_config: Optional[SMTPConfig] = None
    ses_config: Optional[SESConfig] = None