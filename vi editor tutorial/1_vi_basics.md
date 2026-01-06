# VI Editor Mastery: Basic Operations

Welcome to your journey to mastering `vi`. This guide is designed to build your muscle memory.

**Core Concept**: `vi` is a modal editor. You are always in one of several "modes". The most important are **Normal Mode** (for navigation and manipulation) and **Insert Mode** (for typing text).

> [!TIP] > **Golden Rule**: When in doubt, press `Esc`. This ensures you are in **Normal Mode**.

## 1. The Modes

| Mode        | How to Enter     | Description                                         | Visual Cue                      |
| :---------- | :--------------- | :-------------------------------------------------- | :------------------------------ |
| **Normal**  | `Esc`            | The default mode. Used for navigation and commands. | (Usually none, or cursor block) |
| **Insert**  | `i` (and others) | Used for typing text.                               | `-- INSERT --` at bottom        |
| **Command** | `:`              | Used for saving, quitting, and settings.            | `:` at bottom                   |

---

## 2. File Management (Command Mode)

_Perform these from Normal Mode by pressing `:` first._

| Operation       | Command                  | Mnemonic / Tip                         |
| :-------------- | :----------------------- | :------------------------------------- |
| **Save**        | `:w`                     | **W**rite to disk.                     |
| **Quit**        | `:q`                     | **Q**uit.                              |
| **Save & Quit** | `:wq` or `ZZ` (no colon) | Write and Quit. `ZZ` is faster!        |
| **Force Quit**  | `:q!`                    | Quit without saving (discard changes). |
| **Save As**     | `:w filename.txt`        | Write to a new file.                   |

> **Exercise**: Open a new file `vi test.txt`, type some text, save it, and quit. Re-open it.

---

## 3. Navigation (Normal Mode)

_Forget the arrow keys. Keep your hands on the home row._

### Basic Movement

| Key | Direction | Tip                                     |
| :-- | :-------- | :-------------------------------------- |
| `h` | Left      | Index finger.                           |
| `j` | Down      | Middle finger (looks like a hook down). |
| `k` | Up        | Ring finger.                            |
| `l` | Right     | Pinky.                                  |

### Word Movement

| Key | Action                                 | Tip                   |
| :-- | :------------------------------------- | :-------------------- |
| `w` | Jump forward to start of next **w**ord | Faster than `l`.      |
| `b` | Jump **b**ackward to start of word     | Faster than `h`.      |
| `e` | Jump to **e**nd of current word        | Useful for appending. |

### Line Movement

| Key        | Action                              | Tip                                  |
| :--------- | :---------------------------------- | :----------------------------------- |
| `0` (Zero) | Go to start of line                 | Absolute beginning.                  |
| `^`        | Go to first non-blank character     | Often more useful than `0` for code. |
| `$`        | Go to end of line                   | Think of regex anchors.              |
| `gg`       | Go to first line of file            | **G**o **G**o.                       |
| `G`        | Go to last line of file             | Capital G.                           |
| `:n`       | Go to line number `n` (e.g., `:10`) | Jump to specific line.               |

> **Exercise**: Open a large file. Practice moving around using ONLY `h`, `j`, `k`, `l`, `w`, `b`, `gg`, and `G`. Disable your arrow keys if you can!

---

## 4. Entering Insert Mode

_There are many ways to start typing. Choose the one that puts your cursor where you want it._

| Key | Action                      | Mnemonic             |
| :-- | :-------------------------- | :------------------- |
| `i` | Insert **before** cursor    | **I**nsert.          |
| `a` | Insert **after** cursor     | **A**ppend.          |
| `I` | Insert at **start** of line | **I**nsert at start. |
| `A` | Insert at **end** of line   | **A**ppend at end.   |
| `o` | Open new line **below**     | **O**pen below.      |
| `O` | Open new line **above**     | **O**pen above.      |

> **Tip**: `A` is extremely useful for adding semicolons or comments to the end of a line of code.

---

## 5. Basic Editing (Normal Mode)

_Edit text without entering Insert Mode._

| Key        | Action                        | Tip                                                 |
| :--------- | :---------------------------- | :-------------------------------------------------- |
| `x`        | Delete character under cursor | Like the Delete key.                                |
| `r`        | **R**eplace single character  | Press `r` then the new char. No insert mode needed. |
| `u`        | **U**ndo                      | The lifesaver.                                      |
| `Ctrl + r` | **R**edo                      | Opposite of Undo.                                   |
| `dd`       | **D**elete (cut) entire line  | Very common.                                        |
| `yy`       | **Y**ank (copy) entire line   | See Advanced guide for more on copy/paste.          |
| `p`        | **P**aste after cursor        | Pastes the deleted or yanked line.                  |

> **Exercise**: Type a sentence with typos. Use `x` to delete extra chars, `r` to fix wrong chars, and `dd` / `p` to move lines around.


---

## 6. Deleting Text Efficiently (Normal Mode)

_Delete precisely without touching Insert Mode._

### Delete Word

| Key | Action | Tip |
| :-- | :------------------------------ | :----------------------------------------- |
| `dw` | Delete from cursor to end of **w**ord | Most commonly used. |
| `db` | Delete backward to start of word | Useful when cursor is in the middle. |
| `de` | Delete to **e**nd of word | Stops exactly at word end. |
| `diw` | Delete **i**nner **w**ord | Deletes the whole word, cursor anywhere. |
| `daw` | Delete **a** **w**ord (incl. space) | Removes word + trailing space. |

### Delete Line

| Key | Action | Tip |
| :-- | :------------------------------ | :----------------------------------------- |
| `dd` | Delete entire line | Line is cut to buffer. |
| `D` | Delete from cursor to end of line | Same as `d$`. |
| `d0` | Delete from cursor to start of line | Absolute beginning. |
| `d^` | Delete to first non-blank character | Safer for code indentation. |
| `:n,md` | Delete lines from `n` to `m` | Example: `:5,10d`. |

> **Exercise**: Take a paragraph of text. Practice `dw`, `diw`, `dd`, and `D` until you can delete exactly what you want without overthinking.

---
