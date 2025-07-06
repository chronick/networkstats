# App Packaging and Deployment Specification: macOS Application Bundle



## Bundle Structure

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

## Info.plist Configuration

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

## Code Signing

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

## Notarization

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
