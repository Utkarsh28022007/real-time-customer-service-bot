# Troubleshooting and Technical Support

## Account Login Issues
- **Forgotten Password**: Click "Forgot Password" on the login screen and enter your registered email address to receive a secure password reset link valid for 60 minutes.
- **Two-Factor Authentication (2FA)**: If you lost your authenticator device, enter one of your 10-digit emergency backup recovery codes or request account verification via our customer support team.
- **Account Locked**: Accounts are locked for 30 minutes after 5 consecutive failed login attempts as a security precaution.

## Web App and Mobile Performance
- If experiencing interface loading lag or blank screens:
  1. Clear browser cache and cookies (or restart mobile app).
  2. Disable aggressive ad blockers or third-party extensions that may interfere with WebSocket connections.
  3. Ensure your browser is updated to the latest stable release (Chrome 110+, Firefox 110+, Safari 16+, Edge 110+).

## WebSocket Connectivity Drops
- Real-time streaming requires an active persistent WebSocket connection.
- If corporate firewalls or VPNs block port `ws://` / `wss://` protocols, the application gracefully degrades to polling mode or alerts the user to reconnect.
