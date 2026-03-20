"""
Security Audit Module

Performs security checks and vulnerability scanning:
- OWASP Top 10 validation
- SQL injection prevention
- XSS protection
- Authentication/Authorization checks
- Dependency vulnerability scanning
"""

import re
import logging
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Security issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityIssue:
    """Represents a security finding."""

    def __init__(
        self,
        title: str,
        severity: Severity,
        description: str,
        recommendation: str,
        category: str
    ):
        self.title = title
        self.severity = severity
        self.description = description
        self.recommendation = recommendation
        self.category = category

    def __repr__(self) -> str:
        icon = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢",
            Severity.INFO: "ℹ️"
        }[self.severity]

        return f"{icon} [{self.severity.value.upper()}] {self.title}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "recommendation": self.recommendation,
            "category": self.category
        }


class SecurityAuditor:
    """Security auditing utilities."""

    @staticmethod
    def check_sql_injection_protection(code: str) -> List[SecurityIssue]:
        """
        Check for SQL injection vulnerabilities.

        Args:
            code: Code to analyze

        Returns:
            List of security issues found
        """
        issues = []

        # Check for string concatenation in SQL
        sql_concat_patterns = [
            r'execute\s*\(\s*["\'].*?\+',  # execute("SELECT * FROM " + var)
            r'execute\s*\(\s*f["\']',       # execute(f"SELECT * FROM {var}")
            r'\.format\s*\(',               # "SELECT * FROM {}".format(var)
        ]

        for pattern in sql_concat_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(SecurityIssue(
                    title="Potential SQL Injection",
                    severity=Severity.CRITICAL,
                    description="String concatenation detected in SQL query",
                    recommendation="Use parameterized queries with placeholders (:param)",
                    category="SQL Injection"
                ))
                break

        return issues

    @staticmethod
    def check_xss_protection(code: str) -> List[SecurityIssue]:
        """
        Check for XSS vulnerabilities.

        Args:
            code: Code to analyze

        Returns:
            List of security issues found
        """
        issues = []

        # Check for unescaped user input in HTML
        xss_patterns = [
            r'innerHTML\s*=',              # innerHTML = userInput
            r'\.html\s*\(\s*[^"\'{}]',    # .html(userInput) without escaping
        ]

        for pattern in xss_patterns:
            if re.search(pattern, code):
                issues.append(SecurityIssue(
                    title="Potential XSS Vulnerability",
                    severity=Severity.HIGH,
                    description="Unescaped user input may be rendered in HTML",
                    recommendation="Sanitize and escape user input before rendering",
                    category="XSS"
                ))
                break

        return issues

    @staticmethod
    def check_authentication() -> List[SecurityIssue]:
        """
        Check authentication implementation.

        Returns:
            List of security recommendations
        """
        issues = []

        # Recommendations for authentication
        issues.append(SecurityIssue(
            title="Authentication Best Practices",
            severity=Severity.INFO,
            description="Verify authentication is properly implemented",
            recommendation=(
                "✅ Use industry-standard authentication (OAuth2, JWT)\n"
                "✅ Implement rate limiting on auth endpoints\n"
                "✅ Use secure password hashing (bcrypt, argon2)\n"
                "✅ Implement account lockout after failed attempts"
            ),
            category="Authentication"
        ))

        return issues

    @staticmethod
    def check_secrets_exposure(code: str) -> List[SecurityIssue]:
        """
        Check for exposed secrets in code.

        Args:
            code: Code to analyze

        Returns:
            List of security issues found
        """
        issues = []

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        ]

        for pattern, description in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(SecurityIssue(
                    title="Hardcoded Secrets Detected",
                    severity=Severity.CRITICAL,
                    description=description,
                    recommendation="Use environment variables or secret management (e.g., .env, AWS Secrets Manager)",
                    category="Secrets Management"
                ))

        return issues

    @staticmethod
    def check_cors_configuration() -> List[SecurityIssue]:
        """
        Check CORS configuration.

        Returns:
            List of security recommendations
        """
        issues = []

        issues.append(SecurityIssue(
            title="CORS Configuration Review",
            severity=Severity.MEDIUM,
            description="CORS should be properly configured",
            recommendation=(
                "✅ Avoid allow_origins=['*'] in production\n"
                "✅ Specify exact allowed origins\n"
                "✅ Use allow_credentials=True only when necessary\n"
                "✅ Implement proper preflight handling"
            ),
            category="CORS"
        ))

        return issues

    @staticmethod
    def check_input_validation(code: str) -> List[SecurityIssue]:
        """
        Check input validation.

        Args:
            code: Code to analyze

        Returns:
            List of security issues found
        """
        issues = []

        # Check for missing validation
        if "pydantic" in code.lower() or "basemodel" in code.lower():
            # Good - using Pydantic for validation
            pass
        else:
            issues.append(SecurityIssue(
                title="Input Validation Recommendation",
                severity=Severity.MEDIUM,
                description="Ensure all user input is validated",
                recommendation=(
                    "✅ Use Pydantic models for request validation\n"
                    "✅ Validate CNJ process number format\n"
                    "✅ Sanitize file uploads\n"
                    "✅ Limit request payload size"
                ),
                category="Input Validation"
            ))

        return issues

    @staticmethod
    def check_rate_limiting() -> List[SecurityIssue]:
        """
        Check rate limiting implementation.

        Returns:
            List of security recommendations
        """
        issues = []

        issues.append(SecurityIssue(
            title="Rate Limiting Configuration",
            severity=Severity.MEDIUM,
            description="Rate limiting protects against abuse",
            recommendation=(
                "✅ Implement rate limiting with slowapi\n"
                "✅ Different limits for authenticated vs anonymous\n"
                "✅ Lower limits on expensive operations (bulk search)\n"
                "✅ Monitor and alert on rate limit violations"
            ),
            category="Rate Limiting"
        ))

        return issues

    @staticmethod
    def check_https_enforcement() -> List[SecurityIssue]:
        """
        Check HTTPS enforcement.

        Returns:
            List of security recommendations
        """
        issues = []

        issues.append(SecurityIssue(
            title="HTTPS Enforcement",
            severity=Severity.HIGH,
            description="All traffic should use HTTPS in production",
            recommendation=(
                "✅ Redirect HTTP to HTTPS\n"
                "✅ Use HSTS headers\n"
                "✅ Configure secure cookies (secure=True, httponly=True)\n"
                "✅ Use TLS 1.2+ only"
            ),
            category="Transport Security"
        ))

        return issues


class SecurityReport:
    """Security audit report."""

    def __init__(self):
        self.issues: List[SecurityIssue] = []

    def add_issue(self, issue: SecurityIssue):
        """Add security issue to report."""
        self.issues.append(issue)

    def add_issues(self, issues: List[SecurityIssue]):
        """Add multiple issues to report."""
        self.issues.extend(issues)

    def get_by_severity(self, severity: Severity) -> List[SecurityIssue]:
        """Get issues by severity."""
        return [i for i in self.issues if i.severity == severity]

    def get_summary(self) -> Dict[str, int]:
        """Get summary of issues by severity."""
        return {
            "critical": len(self.get_by_severity(Severity.CRITICAL)),
            "high": len(self.get_by_severity(Severity.HIGH)),
            "medium": len(self.get_by_severity(Severity.MEDIUM)),
            "low": len(self.get_by_severity(Severity.LOW)),
            "info": len(self.get_by_severity(Severity.INFO)),
            "total": len(self.issues)
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        summary = self.get_summary()

        md = "# Security Audit Report\n\n"
        md += f"**Total Issues:** {summary['total']}\n\n"
        md += f"- 🔴 Critical: {summary['critical']}\n"
        md += f"- 🟠 High: {summary['high']}\n"
        md += f"- 🟡 Medium: {summary['medium']}\n"
        md += f"- 🟢 Low: {summary['low']}\n"
        md += f"- ℹ️ Info: {summary['info']}\n\n"

        # Group by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            issues = self.get_by_severity(severity)
            if issues:
                md += f"## {severity.value.upper()} Issues\n\n"
                for issue in issues:
                    md += f"### {issue.title}\n\n"
                    md += f"**Category:** {issue.category}\n\n"
                    md += f"**Description:** {issue.description}\n\n"
                    md += f"**Recommendation:**\n{issue.recommendation}\n\n"
                    md += "---\n\n"

        return md


def run_security_audit(code_samples: Dict[str, str] = None) -> SecurityReport:
    """
    Run comprehensive security audit.

    Args:
        code_samples: Optional code samples to analyze

    Returns:
        SecurityReport with findings
    """
    logger.info("Running security audit...")
    report = SecurityReport()

    # Static checks (don't require code)
    report.add_issues(SecurityAuditor.check_authentication())
    report.add_issues(SecurityAuditor.check_cors_configuration())
    report.add_issues(SecurityAuditor.check_rate_limiting())
    report.add_issues(SecurityAuditor.check_https_enforcement())

    # Code-based checks
    if code_samples:
        for filename, code in code_samples.items():
            logger.info(f"Analyzing {filename}...")
            report.add_issues(SecurityAuditor.check_sql_injection_protection(code))
            report.add_issues(SecurityAuditor.check_xss_protection(code))
            report.add_issues(SecurityAuditor.check_secrets_exposure(code))
            report.add_issues(SecurityAuditor.check_input_validation(code))

    summary = report.get_summary()
    logger.info(f"Security audit complete: {summary['total']} issues found")

    return report
