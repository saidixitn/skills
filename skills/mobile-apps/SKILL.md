---
name: mobile-apps
description: >-
  Use when wrapping modern web applications into cross-platform Android and iOS
  native mobile apps using Capacitor, configuring offline service workers, managing
  native permissions, or styling mobile safe-area insets.
---

# Hybrid Mobile App Architecture & Capacitor Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Converting single-page web applications (HTML/JS/PWA) into native Android APKs and iOS apps.
- Configuring **Capacitor** runtime bridges (`capacitor.config.json`).
- Implementing offline caching and background synchronization via Service Workers.
- Managing mobile-specific viewport boundaries, notch safe-area insets, and splash screens.
- Bridging native device capabilities (haptics, camera, local push notifications) to web code.

---

## 2. Hard Architectural Rules

1. **Safe-Area Inset Hygiene**:
   Always declare `viewport-fit=cover` in `<meta name="viewport">` and use CSS environment variables:
   ```css
   body {
     padding-top: env(safe-area-inset-top);
     padding-bottom: env(safe-area-inset-bottom);
   }
   ```
   *Omitting this causes UI buttons and headers to be obscured by the iPhone notch or Android navigation bar.*

2. **Disable User Selection on Touch**:
   Apply `-webkit-user-select: none; user-select: none;` on navigational buttons, tabs, and interactive cards to prevent native text-selection highlight popups during mobile taps.

3. **Atomic Asset Syncing**:
   Always run `npx cap sync` after updating web build output (`dist/` or `www/`) before compiling in Android Studio or Xcode.

---

## 3. Production Code Patterns

### Pattern A: Master Capacitor Configuration (`capacitor.config.json`)
Grounded directly in your `daybook/capacitor.config.json` mobile architecture:

```json
{
  "appId": "com.saidixit.daybook",
  "appName": "Daybook",
  "webDir": "www",
  "bundledWebRuntime": false,
  "server": {
    "androidScheme": "https"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 1500,
      "backgroundColor": "#0a0a0a",
      "showSpinner": false
    }
  }
}
```

---

## 4. Verification Command
Sync web assets and verify native project health:
```bash
npx cap doctor
```
