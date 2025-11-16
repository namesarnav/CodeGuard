"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Severity(str, Enum):
    """Vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueType(str, Enum):
    """Issue type categories."""

    VULNERABILITY = "vulnerability"
    CODE_REVIEW = "code_review"
    AUTO_COMMENT = "auto_comment"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


class ScanStatus(str, Enum):
    """Scan status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Location(BaseModel):
    """Code location information."""

    file_path: str
    start_line: int
    end_line: int
    start_column: Optional[int] = None
    end_column: Optional[int] = None
    function_name: Optional[str] = None


class Issue(BaseModel):
    """Security issue or code review finding."""

    id: str
    type: IssueType
    severity: Severity
    title: str
    description: str
    location: Location
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    fixed_code: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScanRequest(BaseModel):
    """Request to scan a repository."""

    repository_url: Optional[HttpUrl] = None
    repository_path: Optional[str] = None
    branch: Optional[str] = None
    file_paths: Optional[List[str]] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


class ScanResponse(BaseModel):
    """Response from scan operation."""

    scan_id: str
    status: ScanStatus
    repository_url: Optional[str] = None
    repository_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_files: int = 0
    scanned_files: int = 0
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = Field(default_factory=dict)
    error: Optional[str] = None


class ScanResult(BaseModel):
    """Complete scan result with issues."""

    scan_id: str
    status: ScanStatus
    repository_url: Optional[str] = None
    repository_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_files: int
    scanned_files: int
    issues: List[Issue]
    summary: Dict[str, Any] = Field(default_factory=dict)


class ReportFormat(str, Enum):
    """Report export formats."""

    JSON = "json"
    SARIF = "sarif"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request to export scan report."""

    scan_id: str
    format: ReportFormat
    include_code_snippets: bool = True
    include_suggestions: bool = True


class User(BaseModel):
    """User information."""

    id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    """Authentication response."""

    access_token: str
    token_type: str = "bearer"
    user: User

