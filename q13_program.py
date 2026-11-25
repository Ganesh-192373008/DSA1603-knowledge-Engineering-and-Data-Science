# Q13: Rule-based expert system for home-printer troubleshooting
import sys

def ask(question, options):
    while True:
        ans = input(f"{question} {options}: ").strip().lower()
        if not sys.stdin.isatty():
            print(ans)               # echo the piped answer so the log reads like a session
        if ans in options:
            return ans
        print("  Please answer with one of", options)

print("=== Printer Troubleshooting Expert System ===")
powered   = ask("Is the printer powered on?", ["yes", "no"])
connected = ask("Is the printer connected to the computer?", ["usb", "wifi", "no"])
error     = ask("Is an error light / paper-jam message showing?", ["yes", "no"])

# Facts are collected; each rule is (condition, advice)
facts = {"powered": powered == "yes", "connection": connected, "error": error == "yes"}
rules = [
    (lambda f: not f["powered"],
     "IF printer is off THEN check the power cable and press the power button."),
    (lambda f: f["powered"] and f["connection"] == "no",
     "IF printer is on AND not connected THEN connect it by USB cable or join it to the Wi-Fi network."),
    (lambda f: f["powered"] and f["connection"] == "usb" and not f["error"],
     "IF on AND USB-connected AND no error THEN try another USB cable/port and reinstall the printer driver."),
    (lambda f: f["powered"] and f["connection"] == "wifi" and not f["error"],
     "IF on AND Wi-Fi-connected AND no error THEN confirm the printer and PC are on the same network; restart the router."),
    (lambda f: f["powered"] and f["connection"] != "no" and f["error"],
     "IF on AND connected AND error showing THEN clear any paper jam, check ink/toner and paper tray, then restart the printer."),
]

print("\n--- Diagnosis ---")
fired = [advice for cond, advice in rules if cond(facts)]
for advice in fired:
    print("Suggested action:", advice)
if not fired:
    print("No rule matched. Please contact the manufacturer's support.")
