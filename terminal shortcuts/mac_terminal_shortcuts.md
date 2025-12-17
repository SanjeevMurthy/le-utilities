# MacOS Terminal Shortcuts: The Mac Power User Guide

While the previous guide covered _shell_ shortcuts (which work on Linux too), this guide focuses on keys specific to macOS terminal applications like **Terminal.app** and **iTerm2**. These shortcuts use the **Command (⌘)** key.

---

## 1. Window & Tab Management

_Keep your workspace organized without reaching for the mouse._

### The Shortcuts

| Shortcut           | Action                                |
| :----------------- | :------------------------------------ |
| **⌘ + T**          | Open a new **Tab**                    |
| **⌘ + W**          | Check out (Close) the current **Tab** |
| **⌘ + N**          | Open a new **Window**                 |
| **⌘ + Shift + [**  | Go to **Previous** Tab                |
| **⌘ + Shift + ]**  | Go to **Next** Tab                    |
| **⌘ + 1, 2, 3...** | Jump directly to Tab 1, Tab 2, etc.   |

### 🏋️ Practice Exercises

1.  **Tab Hopping:**
    - Open your terminal.
    - Press **⌘ + T** three times to open 3 new tabs.
    - In Tab 1 type `echo "I am number 1"`.
    - Press **⌘ + Shift + ]** to go to Tab 2. Type `top`.
    - Press **⌘ + 3** to obtain Tab 3.
    - Press **⌘ + W** to close Tab 3.

---

## 2. Text & Clipboard

_Copy and paste works differently in the terminal universe._

### The Shortcuts

| Shortcut  | Action           | Notes                                                                                         |
| :-------- | :--------------- | :-------------------------------------------------------------------------------------------- |
| **⌘ + C** | Copy Selection   | Only works if you have text selected with mouse. Otherwise sends "Interrupt" signal (Ctrl+C). |
| **⌘ + V** | Paste Clipboard  | Pastes text from your Mac clipboard into the terminal.                                        |
| **⌘ + A** | Select All       | Selects all text in the terminal buffer (output history).                                     |
| **⌘ + K** | Clear Scrollback | Clears screen _and_ scrollback history. `Ctrl+L` only clears visual screen.                   |

### 🏋️ Practice Exercises

1.  **Copy-Paste Relay:**
    - Open a browser or text editor, copy some text (e.g., a URL).
    - Switch to Terminal (Use **⌘ + Tab**!).
    - Type `wget ` (space at end).
    - Press **⌘ + V** to paste the URL.
2.  **The Nuclear Clean:**
    - Run `ls -R /` (Let it run for a second then Ctrl+C). Screen is messy.
    - Press **⌘ + K**. Gone forever.

---

## 3. View & Search

_Zoom in for presentations or find that error in the logs._

### The Shortcuts

| Shortcut          | Action                               |
| :---------------- | :----------------------------------- |
| **⌘ + Plus (+)**  | Increase Font Size (Zoom In)         |
| **⌘ + Minus (-)** | Decrease Font Size (Zoom Out)        |
| **⌘ + 0**         | Reset Font Size to Default           |
| **⌘ + F**         | Find / Search within Terminal Output |
| **⌘ + G**         | Find Next occurrence                 |

### 🏋️ Practice Exercises

1.  **Detective Mode:**
    - Run `dmesg` or `cat` a large log file.
    - Press **⌘ + F**.
    - Type `error` or `warning`.
    - Press **Enter** and use **⌘ + G** to jump to the next match.
2.  **Presentation Time:**
    - Press **⌘ + +** three times to make text huge.
    - Press **⌘ + 0** to go back to normal.

---

## 4. Mac-Specific Navigation Tricks

_Using Option (Alt) key for faster movement._

By default, macOS Terminal might not treat **Option (⌥)** as the "Meta" key perfectly.

- **Option + Left Arrow**: Move cursor back one word.
- **Option + Right Arrow**: Move cursor forward one word.
- **Fn + Left Arrow**: Scroll to Top (Home).
- **Fn + Right Arrow**: Scroll to Bottom (End).

> **Tip:** If Option+Arrows print weird symbols (like `[D` or `[C`), go to **Terminal > Search Settings > Profiles > Keyboard** and map Option key to "Use Option as Meta Key" if available, or check unique app settings.

---

## 5. Editing & Command Line Cleanup

_Fix mistakes fast using Mac-style combinations._

While the standard `Ctrl` shortcuts work, many Mac users prefer these alternatives if configured:

| Shortcut                    | Action                       | Notes                                                                     |
| :-------------------------- | :--------------------------- | :------------------------------------------------------------------------ |
| **Option (⌥) + Delete (⌫)** | Delete **word** backward     | Similar to `Ctrl+W`. Requires "Option as Meta" setting.                   |
| **Fn + Delete**             | Delete **character** forward | Acts like the "Del" key on PC keyboards.                                  |
| **Ctrl + U**                | Clear entire line (to start) | Best way to "clear the command typed" instantly.                          |
| **Ctrl + C**                | Cancel command               | Aborts the current line or running process.                               |
| **Ctrl + \_** (Underscore)  | **Undo** last edit           | Terminal's version of `Cmd+Z`. `Cmd+Z` often does _nothing_ in the shell! |

### 🏋️ Practice Exercises

1.  **The Mac Delete:**
    - Type `git commit -m "wrong message"`.
    - Hold **Option** and press **Delete** twice to remove the quote and the message words.
2.  **Oops, Undo:**
    - Type `dangerous_command`.
    - Press **Ctrl + U** to wipe it before you accidentally hit Enter.
    - Type `rm -rf /important`.
    - Press **Ctrl + \_** (Shift + -) to undo typing that.

---

## Summary Checklist

- [ ] Mastered switching tabs with **⌘ + Shift + ]**
- [ ] Used **Option + Delete** to erase words
- [ ] Used **Ctrl + U** to clear a bad command
- [ ] Used **⌘ + K** to clear messy output
- [ ] Used **⌘ + F** instead of scrolling manually
- [ ] Copied a command with **⌘ + C** and pasted with **⌘ + V**

Enjoy your Mac Terminal superpowers!
