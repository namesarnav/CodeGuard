"""Code ingestion from GitHub repositories and local directories."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

import git
from github import Github
from git import Repo

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".php",
    ".rb",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".dockerfile",
    ".tf",
    ".tfvars",
}

# Directories to ignore
IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "target",  # Rust
    "vendor",  # Go
    ".idea",
    ".vscode",
}


class CodeIngestion:
    """Handle code ingestion from various sources."""

    def __init__(self) -> None:
        """Initialize code ingestion."""
        self.github: Optional[Github] = None
        if settings.github_pat:
            self.github = Github(settings.github_pat)

    async def clone_repository(
        self,
        repository_url: str,
        branch: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Clone a GitHub repository.

        Args:
            repository_url: GitHub repository URL
            branch: Branch to clone (default: default branch)
            output_dir: Output directory (default: temp directory)

        Returns:
            Path to cloned repository
        """
        logger.info("Cloning repository", url=repository_url, branch=branch)

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="codeguard_")

        try:
            repo = Repo.clone_from(
                repository_url,
                output_dir,
                branch=branch,
                depth=1,
            )
            logger.info("Repository cloned", path=output_dir, branch=repo.active_branch.name)
            return output_dir
        except git.exc.GitCommandError as e:
            logger.error("Failed to clone repository", error=str(e))
            raise

    async def scan_directory(
        self,
        directory: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Scan directory for code files.

        Args:
            directory: Directory to scan
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            List of file information dictionaries
        """
        logger.info("Scanning directory", path=directory)
        files = []

        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        for root, dirs, filenames in os.walk(directory_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in filenames:
                file_path = Path(root) / filename

                # Check if file extension is supported
                if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                # Check include/exclude patterns
                relative_path = file_path.relative_to(directory_path)
                if exclude_patterns and any(
                    self._match_pattern(str(relative_path), pattern)
                    for pattern in exclude_patterns
                ):
                    continue

                if include_patterns and not any(
                    self._match_pattern(str(relative_path), pattern)
                    for pattern in include_patterns
                ):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception as e:
                    logger.warning("Failed to read file", path=str(file_path), error=str(e))
                    continue

                files.append(
                    {
                        "path": str(relative_path),
                        "absolute_path": str(file_path),
                        "content": content,
                        "language": self._detect_language(file_path.suffix),
                        "size": len(content),
                        "lines": content.count("\n") + 1,
                    }
                )

        logger.info("Directory scan complete", files_found=len(files))
        return files

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match file path against pattern (supports glob)."""
        from fnmatch import fnmatch

        return fnmatch(path, pattern)

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".php": "php",
            ".rb": "ruby",
            ".sh": "shell",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".dockerfile": "dockerfile",
            ".tf": "terraform",
            ".tfvars": "terraform",
        }
        return language_map.get(extension.lower(), "unknown")

    def cleanup(self, directory: str) -> None:
        """Clean up temporary directory."""
        if os.path.exists(directory) and directory.startswith(tempfile.gettempdir()):
            try:
                shutil.rmtree(directory)
                logger.info("Cleaned up temporary directory", path=directory)
            except Exception as e:
                logger.warning("Failed to cleanup directory", path=directory, error=str(e))

