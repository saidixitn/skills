import Cocoa

// Swift Menu Bar Status Item Template
class StatusItemController {
    var statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    init() {
        statusItem.button?.title = "● Live"
    }
}
