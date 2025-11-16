"""Main scanner orchestrator."""

import uuid
from datetime import datetime
from typing import List, Optional

from app.core.ingestion import CodeIngestion
from app.core.llm import LLMEngine
from app.models.schemas import Issue, IssueType, Location, ScanResult, ScanStatus, Severity
from app.rag.chunker import CodeChunker
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.core.logging import get_logger

logger = get_logger(__name__)


class CodeScanner:
    """Main code scanner orchestrator."""

    def __init__(self) -> None:
        """Initialize scanner components."""
        self.ingestion = CodeIngestion()
        self.chunker = CodeChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.llm = LLMEngine()

    async def scan(
        self,
        repository_url: Optional[str] = None,
        repository_path: Optional[str] = None,
        branch: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> ScanResult:
        """
        Scan a repository for vulnerabilities and code issues.

        Args:
            repository_url: GitHub repository URL
            repository_path: Local repository path
            branch: Branch to scan
            file_paths: Specific file paths to scan
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            ScanResult with all findings
        """
        scan_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        logger.info("Starting scan", scan_id=scan_id, repository_url=repository_url)

        try:
            # Step 1: Ingest code
            if repository_url:
                repo_path = await self.ingestion.clone_repository(
                    repository_url, branch=branch
                )
            elif repository_path:
                repo_path = repository_path
            else:
                raise ValueError("Either repository_url or repository_path must be provided")

            # Step 2: Scan directory
            files = await self.ingestion.scan_directory(
                repo_path,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )

            if file_paths:
                files = [f for f in files if f["path"] in file_paths]

            total_files = len(files)
            logger.info("Files to scan", count=total_files, scan_id=scan_id)

            # Step 3: Chunk and embed files
            all_chunks = []
            all_embeddings = []

            for file_info in files:
                chunks = self.chunker.chunk_file(
                    file_info["content"],
                    file_info["path"],
                    file_info["language"],
                    metadata={"file_size": file_info["size"], "lines": file_info["lines"]},
                )
                all_chunks.extend(chunks)

            # Generate embeddings
            chunk_texts = [chunk["content"] for chunk in all_chunks]
            embeddings = self.embedder.generate_embeddings(chunk_texts)

            # Step 4: Store in vector database
            self.vector_store.add_chunks(all_chunks, embeddings, scan_id)

            # Step 5: Analyze each file/chunk
            all_issues = []
            scanned_files = 0

            for file_info in files:
                try:
                    # Get relevant context from vector store
                    file_embedding = self.embedder.generate_embedding(file_info["content"])
                    context = self.vector_store.search(
                        file_embedding,
                        limit=3,
                        filter_dict={"language": file_info["language"]},
                    )

                    # Analyze with LLM
                    analysis = await self.llm.analyze_code(
                        file_info["content"],
                        file_info["language"],
                        file_info["path"],
                        context=context,
                    )

                    # Convert analysis to issues
                    issues = self._convert_analysis_to_issues(
                        analysis, file_info["path"], file_info["language"]
                    )
                    all_issues.extend(issues)
                    scanned_files += 1

                    logger.debug(
                        "File analyzed",
                        file_path=file_info["path"],
                        issues=len(issues),
                        scan_id=scan_id,
                    )
                except Exception as e:
                    logger.error(
                        "Failed to analyze file",
                        file_path=file_info["path"],
                        error=str(e),
                        scan_id=scan_id,
                    )

            completed_at = datetime.utcnow()

            # Calculate summary
            summary = self._calculate_summary(all_issues)

            result = ScanResult(
                scan_id=scan_id,
                status=ScanStatus.COMPLETED,
                repository_url=repository_url,
                repository_path=repository_path,
                started_at=started_at,
                completed_at=completed_at,
                total_files=total_files,
                scanned_files=scanned_files,
                issues=all_issues,
                summary=summary,
            )

            logger.info(
                "Scan completed",
                scan_id=scan_id,
                issues=len(all_issues),
                duration=(completed_at - started_at).total_seconds(),
            )

            # Cleanup
            if repository_url:
                self.ingestion.cleanup(repo_path)

            return result

        except Exception as e:
            logger.error("Scan failed", scan_id=scan_id, error=str(e))
            return ScanResult(
                scan_id=scan_id,
                status=ScanStatus.FAILED,
                repository_url=repository_url,
                repository_path=repository_path,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                total_files=0,
                scanned_files=0,
                issues=[],
                summary={"error": str(e)},
            )

    def _convert_analysis_to_issues(
        self, analysis: dict, file_path: str, language: str
    ) -> List[Issue]:
        """Convert LLM analysis to Issue objects."""
        issues = []

        # Process vulnerabilities
        for vuln in analysis.get("vulnerabilities", []):
            issues.append(
                Issue(
                    id=str(uuid.uuid4()),
                    type=IssueType.VULNERABILITY,
                    severity=Severity(vuln.get("severity", "medium").lower()),
                    title=vuln.get("title", "Security vulnerability"),
                    description=vuln.get("description", ""),
                    location=Location(
                        file_path=file_path,
                        start_line=vuln.get("start_line", 1),
                        end_line=vuln.get("end_line", vuln.get("start_line", 1)),
                        function_name=None,
                    ),
                    rule_id=vuln.get("rule_id"),
                    cwe_id=vuln.get("cwe_id"),
                    owasp_category=vuln.get("owasp_category"),
                    suggestion=vuln.get("suggestion"),
                    code_snippet=vuln.get("code_snippet"),
                    fixed_code=vuln.get("fixed_code"),
                )
            )

        # Process code review findings
        for review in analysis.get("code_review", []):
            issues.append(
                Issue(
                    id=str(uuid.uuid4()),
                    type=IssueType.CODE_REVIEW,
                    severity=Severity(review.get("severity", "info").lower()),
                    title=review.get("title", "Code review finding"),
                    description=review.get("description", ""),
                    location=Location(
                        file_path=file_path,
                        start_line=review.get("start_line", 1),
                        end_line=review.get("end_line", review.get("start_line", 1)),
                    ),
                    suggestion=review.get("suggestion"),
                    code_snippet=review.get("code_snippet"),
                    fixed_code=review.get("fixed_code"),
                )
            )

        # Process auto-comments (convert to code review issues)
        for comment in analysis.get("auto_comments", []):
            issues.append(
                Issue(
                    id=str(uuid.uuid4()),
                    type=IssueType.AUTO_COMMENT,
                    severity=Severity.INFO,
                    title="Suggested comment",
                    description=comment.get("comment", ""),
                    location=Location(
                        file_path=file_path,
                        start_line=comment.get("line", 1),
                        end_line=comment.get("line", 1),
                    ),
                )
            )

        return issues

    def _calculate_summary(self, issues: List[Issue]) -> dict:
        """Calculate summary statistics."""
        summary = {
            "total_issues": len(issues),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "by_type": {
                "vulnerability": 0,
                "code_review": 0,
                "auto_comment": 0,
            },
        }

        for issue in issues:
            summary["by_severity"][issue.severity.value] = (
                summary["by_severity"].get(issue.severity.value, 0) + 1
            )
            summary["by_type"][issue.type.value] = (
                summary["by_type"].get(issue.type.value, 0) + 1
            )

        return summary

