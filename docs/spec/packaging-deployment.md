# App Packaging and Deployment Specification

## Overview

The packaging and deployment process transforms the Python application into a native macOS application bundle, creates distributable DMG installers, and automates the release process through GitHub Actions for both Intel and Apple Silicon architectures.

## Current Implementation

### PyInstaller Configuration

```python
# NetworkStats.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('networkstats', 'networkstats'),
    ],
    hiddenimports=['rumps', 'toga', 'plotly', 'polars'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NetworkStats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='NetworkStats.app',
    icon='assets/NetworkStats.icns',
    bundle_identifier='com.networkstats.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Hide from dock
        'NSRequiresAquaSystemAppearance': False,  # Dark mode support
    },
)
```

## macOS Application Bundle

### Bundle Structure

```
NetworkStats.app/
├── Contents/
│   ├── Info.plist              # Application metadata
│   ├── MacOS/
│   │   └── NetworkStats        # Main executable
│   ├── Resources/
│   │   ├── NetworkStats.icns   # Application icon
│   │   ├── en.lproj/          # Localization
│   │   └── assets/            # Additional resources
│   └── Frameworks/            # Dynamic libraries
```

### Info.plist Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>NetworkStats</string>
    
    <key>CFBundleDisplayName</key>
    <string>Network Stats</string>
    
    <key>CFBundleIdentifier</key>
    <string>com.networkstats.app</string>
    
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    
    <key>CFBundleExecutable</key>
    <string>NetworkStats</string>
    
    <key>CFBundleIconFile</key>
    <string>NetworkStats.icns</string>
    
    <key>LSMinimumSystemVersion</key>
    <string>10.14.0</string>
    
    <key>NSHighResolutionCapable</key>
    <true/>
    
    <key>LSUIElement</key>
    <true/>
    
    <key>NSUserNotificationAlertStyle</key>
    <string>alert</string>
    
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    
    <!-- Permissions -->
    <key>NSNetworkUsageDescription</key>
    <string>Network Stats needs network access to monitor connectivity.</string>
    
    <!-- Launch at login support -->
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
```

### Code Signing

```bash
#!/bin/bash
# scripts/sign_app.sh

APP_PATH="dist/NetworkStats.app"
IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
ENTITLEMENTS="entitlements.plist"

# Create entitlements file
cat > "$ENTITLEMENTS" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <false/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
EOF

# Sign the app
codesign --deep --force --verify --verbose \
    --sign "$IDENTITY" \
    --entitlements "$ENTITLEMENTS" \
    --options runtime \
    "$APP_PATH"

# Verify signature
codesign --verify --verbose "$APP_PATH"
spctl --assess --verbose "$APP_PATH"
```

### Notarization

```bash
#!/bin/bash
# scripts/notarize_app.sh

APP_PATH="dist/NetworkStats.app"
BUNDLE_ID="com.networkstats.app"
USERNAME="developer@example.com"
PASSWORD="@keychain:AC_PASSWORD"
TEAM_ID="TEAM_ID"

# Create ZIP for notarization
ditto -c -k --keepParent "$APP_PATH" "NetworkStats.zip"

# Submit for notarization
xcrun notarytool submit "NetworkStats.zip" \
    --apple-id "$USERNAME" \
    --password "$PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait

# Staple the notarization ticket
xcrun stapler staple "$APP_PATH"
```

## DMG Creation

### DMG Builder Script

```python
#!/usr/bin/env python3
# scripts/create_dmg.py

import os
import subprocess
import tempfile
from pathlib import Path

class DMGBuilder:
    def __init__(self, app_path: str, output_name: str):
        self.app_path = Path(app_path)
        self.output_name = output_name
        self.dmg_path = Path(f"dist/{output_name}.dmg")
        
    def create(self):
        """Create DMG with custom background and layout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create DMG source directory
            source_dir = Path(temp_dir) / "dmg"
            source_dir.mkdir()
            
            # Copy app
            subprocess.run([
                "cp", "-R", 
                str(self.app_path), 
                str(source_dir)
            ])
            
            # Create Applications symlink
            subprocess.run([
                "ln", "-s", 
                "/Applications", 
                str(source_dir / "Applications")
            ])
            
            # Create DMG
            self._create_dmg(source_dir)
            
            # Apply custom appearance
            self._customize_dmg()
            
            # Sign DMG
            self._sign_dmg()
    
    def _create_dmg(self, source_dir: Path):
        """Create initial DMG."""
        subprocess.run([
            "hdiutil", "create",
            "-volname", "NetworkStats",
            "-srcfolder", str(source_dir),
            "-ov",
            "-format", "UDZO",
            str(self.dmg_path)
        ])
    
    def _customize_dmg(self):
        """Apply custom DMG appearance."""
        # AppleScript for DMG customization
        applescript = '''
        tell application "Finder"
            tell disk "NetworkStats"
                open
                set current view of container window to icon view
                set toolbar visible of container window to false
                set statusbar visible of container window to false
                set bounds of container window to {400, 100, 900, 450}
                set position of item "NetworkStats.app" to {100, 200}
                set position of item "Applications" to {400, 200}
                set background picture of container window to file ".background:background.png"
                close
                open
                update without registering applications
                delay 2
            end tell
        end tell
        '''
        
        subprocess.run(["osascript", "-e", applescript])
    
    def _sign_dmg(self):
        """Sign the DMG."""
        subprocess.run([
            "codesign", "--force", "--sign",
            "Developer ID Application: Your Name (TEAM_ID)",
            str(self.dmg_path)
        ])

# Usage
if __name__ == "__main__":
    builder = DMGBuilder("dist/NetworkStats.app", "NetworkStats-1.0.0")
    builder.create()
```

### DMG Background Image

```python
# scripts/create_dmg_background.py
from PIL import Image, ImageDraw, ImageFont

def create_dmg_background():
    """Create custom DMG background image."""
    # Create 500x350 image
    img = Image.new('RGB', (500, 350), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add logo and instructions
    # ... implementation ...
    
    img.save('assets/dmg_background.png')
```

## Universal Binary Support

### Build Script for Universal Binary

```bash
#!/bin/bash
# scripts/build_universal.sh

echo "Building Universal Binary for NetworkStats..."

# Clean previous builds
rm -rf build dist

# Build for Intel
echo "Building for Intel (x86_64)..."
poetry run pyinstaller NetworkStats.spec \
    --distpath dist-intel \
    --workpath build-intel \
    -- --target-arch x86_64

# Build for Apple Silicon
echo "Building for Apple Silicon (arm64)..."
poetry run pyinstaller NetworkStats.spec \
    --distpath dist-arm64 \
    --workpath build-arm64 \
    -- --target-arch arm64

# Create universal binary
echo "Creating Universal Binary..."
mkdir -p dist/NetworkStats.app/Contents/MacOS

lipo -create \
    dist-intel/NetworkStats.app/Contents/MacOS/NetworkStats \
    dist-arm64/NetworkStats.app/Contents/MacOS/NetworkStats \
    -output dist/NetworkStats.app/Contents/MacOS/NetworkStats

# Copy remaining app structure
cp -R dist-intel/NetworkStats.app/Contents/* dist/NetworkStats.app/Contents/
rm -rf dist/NetworkStats.app/Contents/MacOS/NetworkStats
cp dist/NetworkStats.app/Contents/MacOS/NetworkStats dist/NetworkStats.app/Contents/MacOS/

# Sign universal app
./scripts/sign_app.sh

echo "Universal Binary created successfully!"
```

## GitHub Actions Automation

### Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    strategy:
      matrix:
        arch: [x86_64, arm64]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Build for ${{ matrix.arch }}
      run: |
        poetry run pyinstaller NetworkStats.spec \
          -- --target-arch ${{ matrix.arch }}
    
    - name: Sign and Notarize
      env:
        APPLE_ID: ${{ secrets.APPLE_ID }}
        APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
        TEAM_ID: ${{ secrets.TEAM_ID }}
        SIGNING_IDENTITY: ${{ secrets.SIGNING_IDENTITY }}
      run: |
        # Import certificate
        echo "${{ secrets.CERTIFICATE_P12 }}" | base64 --decode > certificate.p12
        security create-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
        security default-keychain -s build.keychain
        security unlock-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
        security import certificate.p12 -k build.keychain \
          -P "${{ secrets.CERTIFICATE_PASSWORD }}" -T /usr/bin/codesign
        security set-key-partition-list -S apple-tool:,apple:,codesign: \
          -s -k "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
        
        # Sign app
        codesign --deep --force --verify --verbose \
          --sign "$SIGNING_IDENTITY" \
          --options runtime \
          "dist/NetworkStats.app"
        
        # Notarize
        ditto -c -k --keepParent "dist/NetworkStats.app" "NetworkStats.zip"
        xcrun notarytool submit "NetworkStats.zip" \
          --apple-id "$APPLE_ID" \
          --password "$APPLE_PASSWORD" \
          --team-id "$TEAM_ID" \
          --wait
        
        xcrun stapler staple "dist/NetworkStats.app"
    
    - name: Create DMG
      run: |
        npm install -g create-dmg
        create-dmg 'dist/NetworkStats.app' dist || true
        mv "NetworkStats $(cat version.txt).dmg" \
           "NetworkStats-$(cat version.txt)-${{ matrix.arch }}.dmg"
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: NetworkStats-${{ matrix.arch }}
        path: "*.dmg"
  
  create-universal:
    needs: build-macos
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
    
    - name: Create Universal DMG
      run: |
        # Extract both architectures
        hdiutil attach NetworkStats-x86_64/*.dmg
        cp -R /Volumes/NetworkStats/NetworkStats.app ./NetworkStats-intel.app
        hdiutil detach /Volumes/NetworkStats
        
        hdiutil attach NetworkStats-arm64/*.dmg
        cp -R /Volumes/NetworkStats/NetworkStats.app ./NetworkStats-arm64.app
        hdiutil detach /Volumes/NetworkStats
        
        # Create universal binary
        mkdir -p NetworkStats.app/Contents/MacOS
        lipo -create \
          NetworkStats-intel.app/Contents/MacOS/NetworkStats \
          NetworkStats-arm64.app/Contents/MacOS/NetworkStats \
          -output NetworkStats.app/Contents/MacOS/NetworkStats
        
        # Copy rest of app
        cp -R NetworkStats-intel.app/Contents/* NetworkStats.app/Contents/
        rm NetworkStats.app/Contents/MacOS/NetworkStats
        cp NetworkStats.app/Contents/MacOS/NetworkStats NetworkStats.app/Contents/MacOS/
        
        # Create final DMG
        create-dmg NetworkStats.app . || true
        mv NetworkStats*.dmg NetworkStats-universal.dmg
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          NetworkStats-universal.dmg
          NetworkStats-x86_64/*.dmg
          NetworkStats-arm64/*.dmg
        draft: false
        prerelease: false
        generate_release_notes: true
```

## Auto-Update System

### Sparkle Integration

```python
# networkstats/updater.py
import subprocess
import json
from pathlib import Path

class AutoUpdater:
    """Handle automatic updates using Sparkle framework."""
    
    APPCAST_URL = "https://github.com/user/network-stats/releases/latest/download/appcast.xml"
    
    def __init__(self):
        self.sparkle_path = Path(__file__).parent / "Sparkle.framework"
        
    def check_for_updates(self):
        """Check for available updates."""
        # Implementation depends on Sparkle integration
        pass
    
    def generate_appcast(self, version: str, release_notes: str):
        """Generate appcast.xml for Sparkle."""
        appcast = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
  <channel>
    <title>NetworkStats Updates</title>
    <link>{self.APPCAST_URL}</link>
    <description>Most recent changes with links to updates.</description>
    <language>en</language>
    <item>
      <title>Version {version}</title>
      <sparkle:releaseNotesLink>
        https://github.com/user/network-stats/releases/tag/v{version}
      </sparkle:releaseNotesLink>
      <pubDate>{self._get_pub_date()}</pubDate>
      <enclosure 
        url="https://github.com/user/network-stats/releases/download/v{version}/NetworkStats-{version}.dmg"
        sparkle:version="{version}"
        type="application/octet-stream"
        sparkle:edSignature="{self._get_signature()}" 
        length="{self._get_file_size()}"
      />
    </item>
  </channel>
</rss>"""
        return appcast
```

## Version Management

### Semantic Versioning

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

## Installation Methods

### Homebrew Cask

```ruby
# Formula/networkstats.rb
cask "networkstats" do
  version "1.0.0"
  sha256 "..." # SHA256 of DMG
  
  url "https://github.com/user/network-stats/releases/download/v#{version}/NetworkStats-#{version}.dmg"
  name "NetworkStats"
  desc "Network uptime monitor for macOS"
  homepage "https://github.com/user/network-stats"
  
  app "NetworkStats.app"
  
  uninstall quit: "com.networkstats.app"
  
  zap trash: [
    "~/Library/Application Support/NetworkStats",
    "~/Library/Preferences/com.networkstats.app.plist",
    "~/.config/networkstats",
  ]
end
```

### Direct Download Landing Page

```html
<!-- docs/install.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Install NetworkStats</title>
    <script>
    function detectArch() {
        // Simple architecture detection
        const userAgent = navigator.userAgent.toLowerCase();
        if (userAgent.includes('intel')) {
            return 'intel';
        } else if (userAgent.includes('arm') || userAgent.includes('apple')) {
            return 'arm64';
        }
        return 'universal';
    }
    
    function downloadApp() {
        const arch = detectArch();
        const version = '1.0.0';
        const url = `https://github.com/user/network-stats/releases/download/v${version}/NetworkStats-${version}-${arch}.dmg`;
        window.location.href = url;
    }
    </script>
</head>
<body onload="downloadApp()">
    <h1>Downloading NetworkStats...</h1>
    <p>If download doesn't start, <a href="#" onclick="downloadApp()">click here</a>.</p>
</body>
</html>
```

## Security Considerations

### Hardening

1. **Code Signing**: All binaries must be signed
2. **Notarization**: Required for macOS 10.15+
3. **Entitlements**: Minimal required permissions
4. **Sandbox**: Consider sandboxing in future
5. **Updates**: Signed update packages only

### Privacy

1. **Local Storage**: All data stored locally
2. **No Telemetry**: No usage tracking
3. **Network Access**: Only for configured targets
4. **Permissions**: Explicit user consent

## Testing Deployment

### Pre-release Checklist

```bash
#!/bin/bash
# scripts/pre_release_check.sh

echo "Pre-release checklist..."

# Version consistency
echo "✓ Checking version consistency..."
./scripts/check_versions.py

# Build test
echo "✓ Testing build process..."
./scripts/build_app.sh

# Code signing
echo "✓ Verifying code signature..."
codesign --verify --verbose dist/NetworkStats.app

# Gatekeeper
echo "✓ Testing Gatekeeper..."
spctl --assess --verbose dist/NetworkStats.app

# DMG creation
echo "✓ Testing DMG creation..."
./scripts/create_dmg.py

# Installation test
echo "✓ Testing installation..."
# ... automated installation test ...

echo "All checks passed! Ready for release."
```

## Future Enhancements

1. **Windows Support**: MSI installer via WiX
2. **Linux Support**: AppImage, Snap, Flatpak
3. **App Store**: Mac App Store distribution
4. **Delta Updates**: Smaller update packages
5. **Rollback**: Automatic rollback on failure
6. **Beta Channel**: Separate beta release track
7. **Crash Reporting**: Sentry integration
8. **Analytics**: Optional, privacy-preserving analytics 