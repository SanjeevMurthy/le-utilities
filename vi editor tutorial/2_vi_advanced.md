# VI Editor Mastery: Advanced Operations

Once you are comfortable with the basics, these advanced tools will make you faster than any GUI editor.

## 1. Visual Mode (Selecting Text)

_Select blocks of text to copy, delete, or change._

| Key        | Mode             | Description                          |
| :--------- | :--------------- | :----------------------------------- |
| `v`        | **Visual**       | Select character by character.       |
| `V`        | **Visual Line**  | Select entire lines.                 |
| `Ctrl + v` | **Visual Block** | Select rectangular blocks (columns). |

**Operations on Selection:**

- `d` : Delete selection.
- `y` : Yank (copy) selection.
- `c` : Change selection (delete and enter Insert Mode).
- `>` / `<` : Indent / Un-indent selection.

> **Tip**: Use `Ctrl + v` to select a column of text (like multiple lines of code indentation) and delete it all at once.

---

## 2. Copy, Cut, and Paste (Registers)

_In vi, "Delete" is actually "Cut"._

| Key  | Action                       | Tip |
| :--- | :--------------------------- | :-- |
| `yy` | **Y**ank (copy) current line |     |
| `yw` | **Y**ank **w**ord            |     |
| `y$` | **Y**ank to end of line      |     |
| `p`  | **P**aste **after** cursor   |     |
| `P`  | **P**aste **before** cursor  |     |
| `dd` | **D**elete (cut) line        |     |
| `dw` | **D**elete (cut) word        |     |

**Advanced: Registers**
By default, `vi` uses a single clipboard. You can use named registers (clipboards) `a-z`.

- `"ayy` : Yank line into register `a`.
- `"ap` : Paste from register `a`.

---

## 3. Search and Replace

_Powerful regex-based searching._

### Searching

| Key        | Action                            | Tip                                      |
| :--------- | :-------------------------------- | :--------------------------------------- |
| `/pattern` | Search **forward** for `pattern`  | Press `Enter` to search.                 |
| `?pattern` | Search **backward** for `pattern` |                                          |
| `n`        | Go to **n**ext match              |                                          |
| `N`        | Go to previous match              |                                          |
| `*`        | Search for word under cursor      | Very useful for finding variable usages. |

### Search and Replace (Substitution)

Format: `:[range]s/old/new/[flags]`

| Command          | Description                                                          |
| :--------------- | :------------------------------------------------------------------- |
| `:s/foo/bar/`    | Replace first 'foo' with 'bar' on **current line**.                  |
| `:s/foo/bar/g`   | Replace **all** 'foo' with 'bar' on **current line** (g = global).   |
| `:%s/foo/bar/g`  | Replace **all** 'foo' with 'bar' in **entire file** (% = all lines). |
| `:%s/foo/bar/gc` | Replace all with **c**onfirmation prompt.                            |

---

## 4. Advanced Editing & Navigation

### Combining Numbers and Commands

Most commands accept a number count.

- `5j` : Move down 5 lines.
- `3w` : Move forward 3 words.
- `d2w` : Delete 2 words.
- `10dd` : Delete 10 lines.

### Markers

Save a cursor position to return to later.

- `ma` : Set marker `a` at current location.
- `'a` : Jump to line of marker `a`.
- `` `a `` : Jump to exact position of marker `a`.

### Repeating Commands

- `.` (Dot) : Repeat the last change.
  - Example: `dw` (delete word) -> move cursor -> `.` (delete word again).

---

## 5. Working with Multiple Files

| Command               | Action                             |
| :-------------------- | :--------------------------------- |
| `:sp filename`        | **Sp**lit window horizontally.     |
| `:vsp filename`       | **V**ertical **sp**lit.            |
| `Ctrl + w`, `w`       | Cycle between windows.             |
| `Ctrl + w`, `h/j/k/l` | Move to specific window.           |
| `:e filename`         | Edit a new file in current buffer. |

---

## 6. Pro Tips for Mac Terminal Users

- **Caps Lock to Esc**: Remap your Caps Lock key to Escape in macOS System Settings. This is a game changer for `vi`.
- **Scrolling**: `Ctrl + u` (Up half page) and `Ctrl + d` (Down half page) are faster than scrolling.
- **Line Numbers**: Type `:set number` to show line numbers. `:set nonumber` to hide.

> **Mastery Exercise**:
>
> 1. Open a code file.
> 2. Use `/` to find a function name.
> 3. Use `V` to select the whole function.
> 4. Use `y` to copy it.
> 5. Open a vertical split `:vsp newfile.txt`.
> 6. Switch window `Ctrl+w l`.
> 7. Paste `p`.
> 8. Save `:w`.
