#!/usr/bin/env python3
"""
Link processing utilities for document-summarizer skill

Provides helper functions for:
- Link validation and parsing
- URL type classification
- Filename generation from URLs
- Batch grouping
"""

import re
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Dict, Tuple


class LinkType:
    """Link type constants"""
    WEB = "web-article"
    GITHUB_PR = "github-pr"
    GITHUB_ISSUE = "github-issue"
    UNKNOWN = "unknown"


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def classify_link(url: str) -> str:
    """
    Classify URL type.

    Args:
        url: URL to classify

    Returns:
        LinkType constant (WEB, GITHUB_PR, GITHUB_ISSUE, UNKNOWN)
    """
    if not validate_url(url):
        return LinkType.UNKNOWN

    if 'github.com' in url:
        if '/pull/' in url:
            return LinkType.GITHUB_PR
        elif '/issues/' in url:
            return LinkType.GITHUB_ISSUE

    return LinkType.WEB


def extract_domain(url: str) -> str:
    """
    Extract domain from URL and simplify to service name.

    Args:
        url: URL to extract domain from

    Returns:
        Simplified domain string (e.g., 'velog' instead of 'velog.io')
    """
    # Domain mapping for common services
    DOMAIN_MAPPING = {
        'velog.io': 'velog',
        'github.com': 'github',
        'medium.com': 'medium',
        'tistory.com': 'tistory',
        'naver.com': 'naver',
        'notion.so': 'notion',
        'substack.com': 'substack',
        'dev.to': 'devto',
        'hashnode.dev': 'hashnode',
        'techcrunch.com': 'techcrunch',
        'nytimes.com': 'nytimes',
        'theverge.com': 'theverge',
        'arstechnica.com': 'arstechnica',
    }

    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Check if domain has a mapping
        if domain in DOMAIN_MAPPING:
            return DOMAIN_MAPPING[domain]

        # Otherwise, return the first part before the TLD
        # e.g., 'example.com' -> 'example', 'blog.example.com' -> 'blog'
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[0] if parts[0] not in ['www', 'blog', 'www'] else parts[1]

        return domain
    except Exception:
        return 'unknown-source'


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize string for use as filename.

    Args:
        name: String to sanitize
        max_length: Maximum length of filename

    Returns:
        Sanitized filename string
    """
    # Remove special characters
    name = re.sub(r'[/\\:*?"<>|]', '', name)

    # Replace spaces with hyphens
    name = name.replace(' ', '-')

    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)

    # Convert to lowercase
    name = name.lower()

    # Remove leading/trailing hyphens
    name = name.strip('-')

    # Truncate to max length
    if len(name) > max_length:
        name = name[:max_length].rstrip('-')

    return name


def generate_filename(url: str, title: str = None) -> str:
    """
    Generate filename from URL and optional title.

    Args:
        url: Source URL
        title: Optional document title

    Returns:
        Generated filename without .md extension
    """
    link_type = classify_link(url)
    domain = extract_domain(url)

    if link_type == LinkType.GITHUB_PR:
        # Extract repo and PR number
        match = re.search(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', url)
        if match:
            owner, repo, pr_num = match.groups()
            return f"github-{owner}-{repo}-{pr_num}"

    elif link_type == LinkType.GITHUB_ISSUE:
        # Extract repo and issue number
        match = re.search(r'github\.com/([^/]+)/([^/]+)/issues/(\d+)', url)
        if match:
            owner, repo, issue_num = match.groups()
            return f"github-{owner}-{repo}-{issue_num}"

    # For web articles, use domain and title
    if title:
        title_slug = sanitize_filename(title, max_length=60)
        return f"{domain}-{title_slug}"
    else:
        # Fallback: domain and timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{domain}-{timestamp}"


def add_timestamp_suffix(filename: str) -> str:
    """
    Add timestamp suffix to filename.

    Args:
        filename: Base filename without extension

    Returns:
        Filename with timestamp suffix
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{filename}-{timestamp}"


def group_links_into_batches(links: List[str], batch_size: int = 5) -> List[List[str]]:
    """
    Group links into batches.

    Args:
        links: List of URLs
        batch_size: Maximum batch size (default: 5)

    Returns:
        List of batches (list of lists)
    """
    batches = []
    for i in range(0, len(links), batch_size):
        batches.append(links[i:i + batch_size])
    return batches


def remove_duplicates(links: List[str]) -> Tuple[List[str], List[str]]:
    """
    Remove duplicate URLs from list.

    Args:
        links: List of URLs (may contain duplicates)

    Returns:
        Tuple of (unique_links, duplicate_links)
    """
    seen = set()
    unique = []
    duplicates = []

    for link in links:
        if link in seen:
            duplicates.append(link)
        else:
            seen.add(link)
            unique.append(link)

    return unique, duplicates


def parse_links_from_text(text: str) -> List[str]:
    """
    Parse URLs from text (space or newline separated).

    Args:
        text: Text containing URLs

    Returns:
        List of extracted URLs
    """
    # Split by whitespace and newlines
    potential_urls = re.split(r'\s+', text.strip())

    # Filter valid URLs
    urls = [url for url in potential_urls if validate_url(url)]

    return urls


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_urls = [
        "https://nytimes.com/2026/01/ai-breakthrough",
        "https://github.com/anthropics/claude/pull/1234",
        "https://github.com/facebook/react/issues/5678",
        "https://techcrunch.com/startup-funding-round",
    ]

    print("Testing link utilities:")
    print("-" * 60)

    for url in test_urls:
        print(f"\nURL: {url}")
        print(f"  Valid: {validate_url(url)}")
        print(f"  Type: {classify_link(url)}")
        print(f"  Domain: {extract_domain(url)}")
        print(f"  Filename: {generate_filename(url, 'Test Article Title')}")

    print("\n" + "-" * 60)
    print("\nBatch grouping test:")
    batches = group_links_into_batches(test_urls, batch_size=2)
    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i}: {len(batch)} links")

    print("\n" + "-" * 60)
    print("\nDuplicate removal test:")
    test_with_dupes = test_urls + [test_urls[0], test_urls[1]]
    unique, dupes = remove_duplicates(test_with_dupes)
    print(f"  Original: {len(test_with_dupes)} links")
    print(f"  Unique: {len(unique)} links")
    print(f"  Duplicates: {len(dupes)} links")
