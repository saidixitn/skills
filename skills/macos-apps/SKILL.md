---
name: macos-apps
description: >-
  Use when architecting native macOS menu bar status items in Swift and Xcode,
  configuring lightweight background polling, managing NSStatusItem menus,
  or building desktop utilities with zero runtime overhead.
---

# Native macOS Menu Bar Utilities Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Building native macOS status bar menu items (`NSStatusItem`) in Swift.
- Developing ultra-lightweight desktop widgets with zero framework overhead.
- Configuring background polling timers that check server status or alerts quietly in the system tray.
- Managing macOS dark/light mode icon switching via template images.

---

## 2. Hard Architectural Rules

1. **Template Images for System Tray**:
   Always mark menu bar icons as template images (`image.isTemplate = true`). This enables macOS to automatically tint the icon black or white based on menu bar translucency.

2. **Background Thread Polling**:
   Never execute network I/O or database checks on the main UI thread. Always fetch data asynchronously in `DispatchQueue.global(qos: .background)` and update status item titles on `DispatchQueue.main`.

---

## 3. Production Code Patterns

### Pattern A: Master Swift Menu Bar AppDelegate
Grounded directly in your `glance/glance` native macOS project:

```swift
import Cocoa

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var timer: Timer?

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Create variable-width menu bar status item
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        if let button = statusItem?.button {
            button.title = "● Dixit"
            button.action = #selector(menuClicked)
        }

        buildMenu()
        startBackgroundPolling()
    }

    func buildMenu() {
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Check System Health", action: #selector(checkHealth), keyEquivalent: "h"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        statusItem?.menu = menu
    }

    func startBackgroundPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 300, repeats: true) { _ in
            DispatchQueue.global(qos: .background).async {
                // Poll server health or alerts in background
                let isHealthy = true
                DispatchQueue.main.async {
                    self.statusItem?.button?.title = isHealthy ? "● Online" : "▲ Alert"
                }
            }
        }
    }

    @objc func checkHealth() {
        // Handle immediate check
    }

    @objc func menuClicked() {
        // Toggle action
    }
}
```
