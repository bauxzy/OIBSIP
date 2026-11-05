"""
SecurePass - Advanced Password Generator
A local desktop utility built with Tkinter and Python's secrets module.
Generated passwords are kept in memory only for the current session.
"""

import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
except ImportError:
    pyperclip = None


class SecurePassApp:
    BG = "#101820"
    PANEL = "#182630"
    PANEL_LIGHT = "#203440"
    TEXT = "#edf3f6"
    MUTED = "#9aabb5"
    ACCENT = "#54c6a3"
    ACCENT_DARK = "#287f69"
    WARNING = "#e7b567"
    DANGER = "#e47777"

    CHARSETS = {
        "Uppercase (A–Z)": string.ascii_uppercase,
        "Lowercase (a–z)": string.ascii_lowercase,
        "Numbers (0–9)": string.digits,
        "Symbols (!@#...)": "!@#$%^&*()-_=+[]{};:,.?/",
    }
    AMBIGUOUS = set("0O1lI")

    def __init__(self, root):
        self.root = root
        self.root.title("SecurePass | Password Generator")
        self.root.geometry("760x690")
        self.root.minsize(680, 620)
        self.root.configure(bg=self.BG)

        self.history = []  # Session-only; intentionally never written to disk.
        self.current_password = ""
        self.length_var = tk.IntVar(value=16)
        self.exclude_ambiguous_var = tk.BooleanVar(value=True)
        self.type_vars = {
            label: tk.BooleanVar(value=(label != "Symbols (!@#...)"))
            for label in self.CHARSETS
        }

        self._configure_styles()
        self._build_ui()
        self.root.bind("<Return>", lambda _event: self.generate_password())

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Secure.Horizontal.TProgressbar",
            troughcolor=self.PANEL_LIGHT,
            background=self.ACCENT,
            bordercolor=self.PANEL_LIGHT,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
        )
        style.configure(
            "Secure.TScale",
            background=self.PANEL,
            troughcolor=self.PANEL_LIGHT,
        )

    def _build_ui(self):
        outer = tk.Frame(self.root, bg=self.BG, padx=30, pady=24)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=self.BG)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(
            header, text="SECUREPASS", bg=self.BG, fg=self.ACCENT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text="Password generator", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w", pady=(4, 2))
        tk.Label(
            header, text="Create strong passwords, with control over every character.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w")

        result_card = self._card(outer)
        result_card.pack(fill="x", pady=(0, 16))
        tk.Label(
            result_card, text="YOUR PASSWORD", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        result_row = tk.Frame(result_card, bg=self.PANEL)
        result_row.pack(fill="x", pady=(10, 8))
        self.password_var = tk.StringVar(value="Click Generate to create a password")
        self.password_entry = tk.Entry(
            result_row, textvariable=self.password_var, state="readonly",
            readonlybackground=self.PANEL_LIGHT, fg=self.TEXT, insertbackground=self.TEXT,
            relief="flat", font=("Consolas", 15), bd=0
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 10))
        self.copy_button = self._button(result_row, "Copy", self.copy_password, primary=False)
        self.copy_button.pack(side="right", ipady=7)

        strength_row = tk.Frame(result_card, bg=self.PANEL)
        strength_row.pack(fill="x", pady=(3, 0))
        tk.Label(
            strength_row, text="Password strength", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left")
        self.strength_label = tk.Label(
            strength_row, text="Not generated", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        )
        self.strength_label.pack(side="right")
        self.strength_bar = ttk.Progressbar(
            result_card, style="Secure.Horizontal.TProgressbar",
            maximum=100, value=0, length=100
        )
        self.strength_bar.pack(fill="x", pady=(8, 0))

        settings = tk.Frame(outer, bg=self.BG)
        settings.pack(fill="x", pady=(0, 16))
        left = self._card(settings)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = self._card(settings)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(left, text="PASSWORD LENGTH", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        length_line = tk.Frame(left, bg=self.PANEL)
        length_line.pack(fill="x", pady=(12, 5))
        self.length_value_label = tk.Label(
            length_line, text="16 characters", bg=self.PANEL, fg=self.TEXT,
            font=("Segoe UI", 13, "bold")
        )
        self.length_value_label.pack(side="left")
        self.length_scale = tk.Scale(
            left, from_=8, to=64, orient="horizontal", variable=self.length_var,
            command=self._update_length_label, showvalue=False, resolution=1,
            bg=self.PANEL, fg=self.TEXT, troughcolor=self.PANEL_LIGHT,
            activebackground=self.ACCENT, highlightthickness=0, bd=0,
            sliderrelief="flat"
        )
        self.length_scale.pack(fill="x", pady=(0, 2))
        tk.Label(left, text="Minimum 8 · Maximum 64", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w")

        tk.Label(right, text="CHARACTER TYPES", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        for label, variable in self.type_vars.items():
            cb = tk.Checkbutton(
                right, text=label, variable=variable, bg=self.PANEL, fg=self.TEXT,
                activebackground=self.PANEL, activeforeground=self.TEXT,
                selectcolor=self.PANEL_LIGHT, font=("Segoe UI", 9),
                relief="flat", highlightthickness=0
            )
            cb.pack(anchor="w", pady=1)

        options = self._card(outer)
        options.pack(fill="x", pady=(0, 16))
        tk.Checkbutton(
            options, text="Exclude ambiguous characters (0, O, 1, l, I)",
            variable=self.exclude_ambiguous_var, bg=self.PANEL, fg=self.TEXT,
            activebackground=self.PANEL, activeforeground=self.TEXT,
            selectcolor=self.PANEL_LIGHT, font=("Segoe UI", 9),
            relief="flat", highlightthickness=0
        ).pack(anchor="w")

        actions = tk.Frame(outer, bg=self.BG)
        actions.pack(fill="x", pady=(0, 17))
        self._button(actions, "Generate password", self.generate_password, primary=True).pack(
            side="left", fill="x", expand=True, ipady=11
        )
        self._button(actions, "Clear", self.clear_password, primary=False).pack(
            side="left", padx=(10, 0), ipady=11
        )

        history_card = self._card(outer)
        history_card.pack(fill="both", expand=True)
        history_header = tk.Frame(history_card, bg=self.PANEL)
        history_header.pack(fill="x")
        tk.Label(history_header, text="RECENTLY GENERATED", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(history_header, text="This session only · last 5", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 8)).pack(side="right")
        self.history_list = tk.Listbox(
            history_card, height=4, bg=self.PANEL_LIGHT, fg=self.TEXT,
            selectbackground=self.ACCENT_DARK, selectforeground="#ffffff",
            relief="flat", bd=0, font=("Consolas", 10),
            highlightthickness=0, activestyle="none"
        )
        self.history_list.pack(fill="both", expand=True, pady=(10, 0))
        self.history_list.bind("<Double-Button-1>", self.copy_history_item)

        footer = tk.Label(
            outer, text="Passwords are generated locally and are not saved to a file.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8)
        )
        footer.pack(anchor="w", pady=(12, 0))

    def _card(self, parent):
        frame = tk.Frame(parent, bg=self.PANEL, padx=18, pady=16,
                         highlightthickness=1, highlightbackground="#263b47")
        return frame

    def _button(self, parent, text, command, primary=True):
        bg = self.ACCENT_DARK if primary else self.PANEL_LIGHT
        fg = "#ffffff" if primary else self.TEXT
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=self.ACCENT, activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            padx=18, pady=7
        )

    def _update_length_label(self, _value=None):
        self.length_value_label.config(text=f"{self.length_var.get()} characters")

    def _selected_charsets(self):
        selected = [
            charset for label, charset in self.CHARSETS.items()
            if self.type_vars[label].get()
        ]
        return selected

    def generate_password(self):
        selected = self._selected_charsets()
        if len(selected) < 2:
            messagebox.showwarning(
                "Choose more character types",
                "Select at least two character types before generating a password."
            )
            return

        length = self.length_var.get()
        if length < 8:
            messagebox.showwarning("Invalid length", "Password length must be at least 8.")
            return

        if self.exclude_ambiguous_var.get():
            selected = ["".join(c for c in group if c not in self.AMBIGUOUS) for group in selected]

        if any(not group for group in selected):
            messagebox.showerror(
                "Character selection unavailable",
                "One selected character type has no characters after ambiguous characters are excluded."
            )
            return

        if length < len(selected):
            messagebox.showwarning(
                "Length too short",
                "Increase the password length to fit at least one character from each selected type."
            )
            return

        # Guarantee at least one character from every selected category.
        password_chars = [secrets.choice(group) for group in selected]
        combined = "".join(selected)
        password_chars.extend(secrets.choice(combined) for _ in range(length - len(password_chars)))
        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        self.current_password = password
        self.password_var.set(password)
        self._update_strength(password, selected)
        self._add_to_history(password)

        # Automatic copy on generation, as required by the task card.
        self._copy_to_clipboard(password, show_feedback=False)

    def _update_strength(self, password, selected):
        length = len(password)
        diversity = len(selected)
        score = min(100, int((length / 32) * 55 + (diversity / 4) * 45))
        if score < 45:
            label, color = "Weak", self.DANGER
        elif score < 75:
            label, color = "Medium", self.WARNING
        else:
            label, color = "Strong", self.ACCENT
        self.strength_bar["value"] = score
        self.strength_label.config(text=label, fg=color)
        self.strength_bar.configure(style="Secure.Horizontal.TProgressbar")

    def _add_to_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item)

    def _copy_to_clipboard(self, password, show_feedback=True):
        try:
            if pyperclip is None:
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                self.root.update()
            else:
                pyperclip.copy(password)
            if show_feedback:
                messagebox.showinfo("Copied", "Password copied to clipboard.")
        except Exception:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                self.root.update()
                if show_feedback:
                    messagebox.showinfo("Copied", "Password copied to clipboard.")
            except Exception as exc:
                messagebox.showerror("Clipboard error", f"Could not copy password.\n\n{exc}")

    def copy_password(self):
        if not self.current_password:
            messagebox.showinfo("Nothing to copy", "Generate a password first.")
            return
        self._copy_to_clipboard(self.current_password, show_feedback=True)

    def copy_history_item(self, _event=None):
        selection = self.history_list.curselection()
        if not selection:
            return
        self._copy_to_clipboard(self.history[selection[0]], show_feedback=True)

    def clear_password(self):
        self.current_password = ""
        self.password_var.set("Click Generate to create a password")
        self.strength_bar["value"] = 0
        self.strength_label.config(text="Not generated", fg=self.MUTED)


def main():
    root = tk.Tk()
    SecurePassApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
