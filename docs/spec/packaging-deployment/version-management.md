# App Packaging and Deployment Specification: Version Management



## Semantic Versioning

# scripts/bump_version.py
import re
import sys
from pathlib import Path

def bump_version(bump_type='patch'):
    """Bump version number."""
    # Read current version
    pyproject = Path('pyproject.toml')
    content = pyproject.read_text()
    
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("Version not found")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    # Bump version
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update files
    update_version_in_files(new_version)
    
    return new_version

def update_version_in_files(version: str):
    """Update version in all relevant files."""
    files_to_update = [
        ('pyproject.toml', r'version = "\d+\.\d+\.\d+"', f'version = "{version}"'),
        ('networkstats/__init__.py', r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{version}"'),
        ('NetworkStats.spec', r"'CFBundleVersion': '\d+\.\d+\.\d+'", f"'CFBundleVersion': '{version}'"),
    ]
    
    for filepath, pattern, replacement in files_to_update:
        path = Path(filepath)
        content = path.read_text()
        updated = re.sub(pattern, replacement, content)
        path.write_text(updated)

```python
# scripts/bump_version.py
import re
import sys
from pathlib import Path

def bump_version(bump_type='patch'):
    """Bump version number."""
    # Read current version
    pyproject = Path('pyproject.toml')
    content = pyproject.read_text()
    
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("Version not found")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    # Bump version
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update files
    update_version_in_files(new_version)
    
    return new_version

def update_version_in_files(version: str):
    """Update version in all relevant files."""
    files_to_update = [
        ('pyproject.toml', r'version = "\d+\.\d+\.\d+"', f'version = "{version}"'),
        ('networkstats/__init__.py', r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{version}"'),
        ('NetworkStats.spec', r"'CFBundleVersion': '\d+\.\d+\.\d+'", f"'CFBundleVersion': '{version}'"),
    ]
    
    for filepath, pattern, replacement in files_to_update:
        path = Path(filepath)
        content = path.read_text()
        updated = re.sub(pattern, replacement, content)
        path.write_text(updated)

```
