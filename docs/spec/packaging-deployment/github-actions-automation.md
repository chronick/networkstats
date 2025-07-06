# App Packaging and Deployment Specification: GitHub Actions Automation



## Release Workflow

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
