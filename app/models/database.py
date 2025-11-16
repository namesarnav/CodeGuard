"""SQLModel database models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Scan(SQLModel, table=True):
    """Scan record in database."""

    __tablename__ = "scans"

    id: Optional[str] = Field(default=None, primary_key=True)
    repository_url: Optional[str] = None
    repository_path: Optional[str] = None
    branch: Optional[str] = None
    status: str = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_files: int = 0
    scanned_files: int = 0
    total_issues: int = 0
    error: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    issues: list["Issue"] = Relationship(back_populates="scan")


class Issue(SQLModel, table=True):
    """Issue record in database."""

    __tablename__ = "issues"

    id: Optional[str] = Field(default=None, primary_key=True)
    scan_id: str = Field(foreign_key="scans.id")
    type: str
    severity: str
    title: str
    description: str
    file_path: str
    start_line: int
    end_line: int
    start_column: Optional[int] = None
    end_column: Optional[int] = None
    function_name: Optional[str] = None
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    fixed_code: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    scan: Scan = Relationship(back_populates="issues")


class User(SQLModel, table=True):
    """User record in database."""

    __tablename__ = "users"

    id: Optional[str] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    github_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

