# Vi/Vim Editor – Quick Reference Guide

A practical guide covering essential Vi/Vim tasks and their shortcut commands.

---

## 1. Move to the Top of the File

Jump the cursor to the very first line of the file.

| Shortcut | Description                                   |
| -------- | --------------------------------------------- |
| `gg`     | Move cursor to the **first line** of the file |
| `1G`     | Same as `gg` — go to line 1                   |
| `:1`     | Command-mode: jump to line 1                  |

---

## 2. Move to the Bottom of the File

Jump the cursor to the very last line of the file.

| Shortcut | Description                                  |
| -------- | -------------------------------------------- |
| `G`      | Move cursor to the **last line** of the file |
| `:$`     | Command-mode: jump to the last line          |

---

## 3. Move to Start of the Line

Place the cursor at the beginning of the current line.

| Shortcut | Description                                             |
| -------- | ------------------------------------------------------- |
| `0`      | Move to the **first character** (column 0) of the line  |
| `^`      | Move to the **first non-blank character** of the line   |
| `Home`   | Move to the start of the line (if terminal supports it) |

---

## 4. Move to End of the Line

Place the cursor at the end of the current line.

| Shortcut | Description                                           |
| -------- | ----------------------------------------------------- |
| `$`      | Move to the **last character** of the line            |
| `End`    | Move to the end of the line (if terminal supports it) |

---

## 5. Delete Previous Word

Delete the word immediately before the cursor.

| Mode       | Shortcut   | Description                                              |
| ---------- | ---------- | -------------------------------------------------------- |
| **Normal** | `db`       | Delete from cursor **backward** to the start of the word |
| **Normal** | `diw`      | Delete the **entire word** under the cursor              |
| **Insert** | `Ctrl + w` | Delete the word before the cursor while typing           |

---

## 6. Delete Next Word

Delete the word immediately after (or under) the cursor.

| Shortcut | Description                                                                     |
| -------- | ------------------------------------------------------------------------------- |
| `dw`     | Delete from cursor to the **start of the next word** (includes trailing space)  |
| `de`     | Delete from cursor to the **end of the current word** (excludes trailing space) |
| `daw`    | Delete the **entire word** including surrounding whitespace                     |

---

## 7. Select and Copy Lines

Vi uses **Visual mode** to select text, and `y` (yank) to copy.

| Shortcut   | Description                                              |
| ---------- | -------------------------------------------------------- |
| `yy`       | **Copy (yank) the current line**                         |
| `3yy`      | Copy **3 lines** starting from the current line          |
| `V`        | Enter **Visual Line mode** — select full lines           |
| `v`        | Enter **Visual mode** — select character by character    |
| `Ctrl + v` | Enter **Visual Block mode** — select a rectangular block |

**Workflow – Select & Copy:**

1. Press `V` to enter Visual Line mode.
2. Use `j` / `k` (or arrow keys) to extend the selection.
3. Press `y` to **yank (copy)** the selected lines.

---

## 8. Paste the Copied Lines

Paste previously yanked (copied) or deleted text.

| Shortcut | Description                                         |
| -------- | --------------------------------------------------- |
| `p`      | **Paste after** the current line / cursor position  |
| `P`      | **Paste before** the current line / cursor position |

---

## 9. Indent Lines

Shift lines to the right (indent) or left (un-indent).

| Shortcut | Description                                       |
| -------- | ------------------------------------------------- |
| `>>`     | **Indent** the current line                       |
| `<<`     | **Un-indent** the current line                    |
| `3>>`    | Indent **3 lines** starting from the current line |
| `>G`     | Indent from current line **to end of file**       |

**Workflow – Indent in Visual Mode:**

1. Press `V` to enter Visual Line mode.
2. Select the lines with `j` / `k`.
3. Press `>` to **indent** or `<` to **un-indent**.
4. Press `.` to repeat the indent action.

---

## 10. Select All Lines

Select the entire content of the file.

| Shortcut | Description                      |
| -------- | -------------------------------- |
| `ggVG`   | Select **all lines** in the file |

**Step-by-step:**

1. `gg` — move to the top of the file.
2. `V` — enter Visual Line mode.
3. `G` — extend selection to the last line.

After selecting all, you can:

- Press `y` to **copy** all lines.
- Press `d` to **delete** all lines.
- Press `>` to **indent** all lines.

---

## 11. View Line Numbers

Display line numbers alongside the file content.

| Command               | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `:set number`         | Show **absolute** line numbers                        |
| `:set nu`             | Short form of `:set number`                           |
| `:set relativenumber` | Show **relative** line numbers (distance from cursor) |
| `:set rnu`            | Short form of `:set relativenumber`                   |
| `:set nonumber`       | **Hide** line numbers                                 |
| `:set nonu`           | Short form of `:set nonumber`                         |

> **Tip:** To make line numbers permanent, add `set number` to your `~/.vimrc` file.

---

## 12. Go to a Line Number (Without Changing Indent)

Jump to a specific line without altering any indentation.

| Shortcut | Description                                           |
| -------- | ----------------------------------------------------- |
| `:42`    | Jump to **line 42** (replace 42 with any line number) |
| `42G`    | Same — jump to **line 42** in Normal mode             |
| `42gg`   | Same — jump to **line 42**                            |

> **Note:** None of these commands modify the file content or indentation. They are purely navigational.

---

## Bonus: Handy Vi/Vim Shortcuts

| Shortcut      | Description                                     |
| ------------- | ----------------------------------------------- |
| `u`           | **Undo** last change                            |
| `Ctrl + r`    | **Redo** last undone change                     |
| `/pattern`    | **Search** forward for `pattern`                |
| `?pattern`    | **Search** backward for `pattern`               |
| `n`           | Jump to **next** search match                   |
| `N`           | Jump to **previous** search match               |
| `:w`          | **Save** the file                               |
| `:q`          | **Quit** Vi                                     |
| `:wq` or `ZZ` | **Save and quit**                               |
| `:q!`         | **Quit without saving**                         |
| `dd`          | **Delete** the current line                     |
| `x`           | **Delete** the character under the cursor       |
| `i`           | Enter **Insert mode** before the cursor         |
| `a`           | Enter **Insert mode** after the cursor          |
| `o`           | Open a **new line below** and enter Insert mode |
| `O`           | Open a **new line above** and enter Insert mode |
| `Esc`         | Return to **Normal mode**                       |
