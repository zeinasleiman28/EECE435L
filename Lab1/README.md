# Lab 1 – Initiation to VS Code, Python and Flask

**EECE 435L – Software Tools Lab** · Zeina Sleiman

## Setup (Windows PowerShell)

```powershell
cd Lab1
py -3 -m venv .venv
.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
```

macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## Running each part

All three parts live in `hello.py`. Older parts are commented out, not deleted. To run one part, uncomment its block and comment out the others.

| Part | Active block in `hello.py` | Command | Expected output |
|------|----------------------------|---------|-----------------|
| 1 – Python | `PART 1` | `python hello.py` | `Roll a dice by Zeina Sleiman!` in the terminal |
| 2 – Flask | `PART 2` | `$env:FLASK_APP = "hello.py"` then `flask run` | `Hello World by Zeina Sleiman!` at http://127.0.0.1:5000/ |
| 3 – Templates | `PART 3` (currently active) | `$env:FLASK_APP = "hello.py"` then `flask run` | Bootstrap navbar + brown heading `Welcome to Flask by Zeina Sleiman!` |

On macOS/Linux, use `export FLASK_APP=hello.py` instead of `$env:FLASK_APP = ...`.

> **Note on `setx`:** The lab sheet uses `setx FLASK_APP "hello.py"`. `setx` saves the variable for *new* terminals only, so the terminal where you ran it won't see it. Either open a new terminal after `setx`, or use `$env:FLASK_APP = "hello.py"`, which applies to the current terminal straight away.

## Part 3 files

- `templates/base.html` – Bootstrap 4.3.1 layout (navbar, `title` and `content` blocks)
- `templates/index.html` – final version extends `base.html`; versions 1 and 2 are kept at the bottom as Jinja comments (`{# ... #}`). HTML comments wouldn't work here because Jinja would still run the tags inside them.
- `static/css/style.css` – heading style (brown, centered, bordered)

## Screenshots

- `screenshots/part1_roll_a_dice.png`
- `screenshots/part2_hello_world.png`
- `screenshots/part3_welcome_to_flask.png`
