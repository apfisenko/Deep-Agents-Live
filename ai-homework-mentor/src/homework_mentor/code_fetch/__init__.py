"""Code fetch package — stage student code without executing it."""

from homework_mentor.code_fetch.github import fetch_github_repository
from homework_mentor.code_fetch.local import fetch_local_directory
from homework_mentor.code_fetch.models import CodeFetchError, FetchResult

__all__ = [
    "CodeFetchError",
    "FetchResult",
    "fetch_github_repository",
    "fetch_local_directory",
]
