# App Packaging and Deployment Specification: DMG Creation



## DMG Builder Script

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

## DMG Background Image

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
