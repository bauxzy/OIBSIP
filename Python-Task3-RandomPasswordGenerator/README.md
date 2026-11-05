# SecurePass — Advanced Password Generator

A small desktop password generator built with Python and Tkinter. It uses Python's `secrets` module rather than `random` for password generation.

## Features

- Password length control from 8 to 64 characters.
- Uppercase, lowercase, numbers and symbols can be selected independently.
- Requires at least two character categories.
- Guarantees at least one character from every selected category.
- Optional exclusion of ambiguous characters (`0`, `O`, `1`, `l`, `I`).
- Strength indicator based on length and selected character diversity.
- Copies each newly generated password to the clipboard automatically.
- Keeps only the five most recent passwords in memory during the current session.
- No password history is written to disk.

## Requirements

- Python 3.10 or newer
- Tkinter (included with most standard Windows Python installations)
- `pyperclip`

## Setup on Windows

Open a terminal in this project folder and run:

```bash
py -m pip install -r requirements.txt
py main.py
```

If the `py` command is unavailable, use:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Usage

1. Choose a password length.
2. Select at least two character categories.
3. Optionally enable the ambiguous-character filter.
4. Select **Generate password**.
5. The generated password is displayed and copied to the clipboard.
6. Double-click an item in the recent list to copy it again.

## Security and privacy

Password generation happens locally using Python's `secrets` module. The app does not send passwords to a server and does not save them to a file. The five-item history exists only in application memory and disappears when the app closes. A copied password remains in the operating system clipboard until another application replaces it or the clipboard is cleared.

The strength label is a simple usability estimate based on password length and selected character categories. It is not a formal password-audit or entropy certification.

## Project structure

```text
Python-Task3-RandomPasswordGenerator/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Internship task

Oasis Infobyte — Python Programming Track  
Task 3: Random Password Generator — Advanced Tier
