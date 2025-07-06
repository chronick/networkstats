# App Packaging and Deployment Specification: Installation Methods



## Homebrew Cask

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

## Direct Download Landing Page

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
