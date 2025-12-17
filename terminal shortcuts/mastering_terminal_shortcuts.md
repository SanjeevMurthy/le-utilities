# Mastering Linux/Mac Terminal Shortcuts: A Practice Guide

Welcome to your guide for mastering terminal shortcuts! Learning these keystrokes will significantly speed up your workflow, reduce typing errors, and make you feel like a terminal wizard.

This guide is structured by category. Each section introduces key shortcuts followed by **exercises** to build muscle memory.

---

## 1. Cursor Navigation

_Stop hitting the arrow keys repeatedly! Use these to jump around quickly._

### The Shortcuts

| Shortcut                     | Action                                                   | Mnemonic          |
| :--------------------------- | :------------------------------------------------------- | :---------------- |
| **Ctrl + A**                 | Go to the **start** of the line                          | **A**head (start) |
| **Ctrl + E**                 | Go to the **end** of the line                            | **E**nd           |
| **Alt + F** (or Esc, then F) | Move **forward** by one word                             | **F**orward       |
| **Alt + B** (or Esc, then B) | Move **backward** by one word                            | **B**ackward      |
| **Ctrl + XX**                | Toggle cursor between start of line and current position | (Cross-Cross)     |

> **Note for Mac Users:** If `Alt` key doesn't work, you may need to configure "Use Option as Meta key" in your terminal settings, or press `Esc` then the letter key.

### 🏋️ Practice Exercises

1.  **Start/End Jumping:**
    - Type: `echo "This is a really long command that I am typing"` (Do not press Enter).
    - Press **Ctrl + A** to go to the start. Adding `sudo ` at the beginning.
    - Press **Ctrl + E** to go to the end. Add ` >> output.txt`.
2.  **Word Jumping:**
    - Type: `cd /var/www/html/project/assets/images`
    - Use **Alt + B** to jump back to `project`.
    - Change `project` to `backup` (delete and retype).
    - Use **Alt + F** to jump forward to the end.

---

## 2. Editing Text

_Deleting character-by-character is too slow. Cut text in chunks._

### The Shortcuts

| Shortcut                   | Action                                          | Mnemonic                  |
| :------------------------- | :---------------------------------------------- | :------------------------ |
| **Ctrl + U**               | Cut everything from cursor to **start** of line | **U**ndo (entire lineish) |
| **Ctrl + K**               | Cut everything from cursor to **end** of line   | **K**ill                  |
| **Ctrl + W**               | Cut the **word** before the cursor              | **W**ord                  |
| **Alt + D**                | Cut the **word** after the cursor               | **D**elete word           |
| **Ctrl + Y**               | **Paste** (Yank) the last cut text              | **Y**ank back             |
| **Ctrl + \_** (underscore) | Undo the last key press                         |                           |

### 🏋️ Practice Exercises

1.  **Quick Fix:**
    - Type: `git coomit -m "Fixed the bug"` (Scanning... typo detected 'coomit').
    - Press **Ctrl + W** three times to delete `"Fixed the bug"`, `-m`, and `coomit`.
    - Type `commit -m "Fixed the bug"`.
2.  **Cut and Paste:**
    - Type: `mv file1.txt file2.txt /home/user/documents/`
    - Oops, you forgot to create the directory first.
    - Press **Ctrl + U** to cut the entire line.
    - Type `mkdir -p /home/user/documents/`. Press Enter.
    - Press **Ctrl + Y** to paste your previous command back. Press Enter.

---

## 3. History Management

_Stop typing the same commands over and over._

### The Shortcuts

| Shortcut     | Action           | Description                                                                                         |
| :----------- | :--------------- | :-------------------------------------------------------------------------------------------------- |
| **Ctrl + R** | Reverse Search   | Start typing a previously used command to find it. Press **Ctrl+R** again to cycle through matches. |
| **!!**       | Previous Command | Runs the very last command again. Useful with `sudo`.                                               |
| **!$**       | Last Argument    | Pastes the last argument of the previous command.                                                   |
| **!n**       | Command N        | Runs command number `n` from your `history`.                                                        |

### 🏋️ Practice Exercises

1.  **Sudo Magic:**
    - Type: `apt-get install python3`
    - Output: _Permission denied_.
    - Type: `sudo !!` (Expands to `sudo apt-get install python3`).
2.  **Argument Reuse:**
    - Type: `mkdir /tmp/project-v1`
    - Type: `cd !$` (Expands to `cd /tmp/project-v1`).
3.  **Search History:**
    - Press **Ctrl + R**.
    - Type `git`. Watch it find your last git command.
    - Press **Ctrl + R** again to find an earlier git command.
    - Press **Enter** to run it, or **Right Arrow** to edit it.

---

## 4. Process Control

_Take control of running programs._

### The Shortcuts

| Shortcut     | Action             | Description                                              |
| :----------- | :----------------- | :------------------------------------------------------- |
| **Ctrl + C** | Interrupt          | Kill the current running process immediately.            |
| **Ctrl + Z** | Suspend            | Pause the current process and send it to the background. |
| **Ctrl + D** | End of File / Exit | Closes the terminal or exits the current shell session.  |
| **Ctrl + L** | Clear Screen       | Clears the terminal screen (same as typing `clear`).     |

### 🏋️ Practice Exercises

1.  **Stopping Runaway Processes:**
    - Type: `ping google.com` (It will run forever).
    - Press **Ctrl + C** to stop it.
2.  **Backgrounding:**
    - Type: `vi newfile.txt`.
    - Press **Ctrl + Z**. use `fg` to bring it back later.
3.  **Clean Slate:**
    - Your screen is full of text? Press **Ctrl + L** to clear it instantly.

---

## 5. Daily Routine Checklist

To maximize retention, try to use at least one new shortcut every day.

- [ ] Used **Ctrl + R** instead of pressing Up arrow 20 times.
- [ ] Used **Ctrl + W** to delete a wrong argument.
- [ ] Used **Alt + B / F** to edit a path in the middle of a command.
- [ ] Used **!$** to cd into a directory I just created.

Happy Hacking!
