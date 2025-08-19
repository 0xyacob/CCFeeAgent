module.exports = {
  version: "3.7.0",
  title: "CC Fee Letter Agent",
  description: "Professional fee letter generation and email automation for CC Growth EIS Fund",
  icon: "icon.png",
  menu: async (kernel, info) => {
    let installed = info.exists("env")
    let running = info.running("start.json")
    
    if (running) {
      let memory = info.local("start.json")
      let url = "http://localhost:8505"
      
      return [{
        default: true,
        icon: "fa-solid fa-desktop",
        text: "Open Fee Letter Agent",
        href: url
      }, {
        icon: "fa-solid fa-terminal",
        text: "Terminal",
        href: "start.json"
      }, {
        icon: "fa-solid fa-gear",
        text: "Settings",
        menu: [{
          icon: "fa-solid fa-folder-open",
          text: "Configure Data Source",
          href: url + "?tab=settings"
        }, {
          icon: "fa-solid fa-envelope",
          text: "Test Email Connection", 
          href: url + "?tab=healthcheck"
        }]
      }]
    } else if (installed) {
      return [{
        default: true,
        icon: "fa-solid fa-power-off",
        text: "Start Fee Letter Agent",
        href: "start.json"
      }, {
        icon: "fa-solid fa-rocket",
        text: "Start Simple Version",
        href: "start_simple.json"
      }, {
        icon: "fa-solid fa-flask",
        text: "Test Ultra-Simple Startup",
        href: "start_test.json"
      }, {
        icon: "fa-solid fa-bug",
        text: "Debug Startup Issues",
        href: "start_debug.json"
      }, {
        icon: "fa-solid fa-vial",
        text: "Run Diagnostic Test",
        href: "test.json"
      }, {
        icon: "fa-solid fa-rotate",
        text: "Update Dependencies",
        href: "update.json"
      }, {
        icon: "fa-solid fa-broom",
        text: "Clean Up Files",
        href: "cleanup.json"
      }, {
        icon: "fa-solid fa-plug",
        text: "Reinstall",
        href: "install.json"
      }]
    } else {
      return [{
        default: true,
        icon: "fa-solid fa-download",
        text: "Install Fee Letter Agent",
        href: "install.json"
      }]
    }
  }
}