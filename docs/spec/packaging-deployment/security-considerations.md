# App Packaging and Deployment Specification: Security Considerations

## Hardening
**Code Signing**: All binaries must be signed
**Notarization**: Required for macOS 10.15+
**Entitlements**: Minimal required permissions
**Sandbox**: Consider sandboxing in future
**Updates**: Signed update packages only

## Privacy
**Local Storage**: All data stored locally
**No Telemetry**: No usage tracking
**Network Access**: Only for configured targets
**Permissions**: Explicit user consent
