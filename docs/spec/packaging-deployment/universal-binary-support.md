# App Packaging and Deployment Specification: Universal Binary Support



## Build Script for Universal Binary

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
