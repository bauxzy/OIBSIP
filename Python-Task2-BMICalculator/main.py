
import tkinter as tk
from tkinter import messagebox


def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height_cm = float(height_entry.get())

        if weight <= 0 or height_cm <= 0:
            raise ValueError

        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"

        result_label.config(
            text=f"Your BMI: {bmi:.2f}\nCategory: {category}"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Enter valid positive numbers for weight and height."
        )


def reset_fields():
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    result_label.config(
        text="Enter your details and calculate your BMI."
    )


# Main window
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("420x380")
root.resizable(False, False)
root.configure(bg="#F2F5F9")

# Heading
tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 22, "bold"),
    bg="#F2F5F9",
    fg="#24324A"
).pack(pady=(25, 8))

tk.Label(
    root,
    text="Calculate your Body Mass Index",
    font=("Arial", 10),
    bg="#F2F5F9",
    fg="#5B6575"
).pack(pady=(0, 20))

# Weight input
tk.Label(
    root,
    text="Weight (kg)",
    font=("Arial", 11, "bold"),
    bg="#F2F5F9",
    fg="#24324A"
).pack()

weight_entry = tk.Entry(
    root, font=("Arial", 12), justify="center", width=25
)
weight_entry.pack(pady=(5, 14), ipady=5)

# Height input
tk.Label(
    root,
    text="Height (cm)",
    font=("Arial", 11, "bold"),
    bg="#F2F5F9",
    fg="#24324A"
).pack()

height_entry = tk.Entry(
    root, font=("Arial", 12), justify="center", width=25
)
height_entry.pack(pady=(5, 18), ipady=5)

# Result label is created before the functions use it
result_label = tk.Label(
    root,
    text="Enter your details and calculate your BMI.",
    font=("Arial", 12, "bold"),
    bg="#F2F5F9",
    fg="#24324A",
    justify="center"
)
result_label.pack(pady=24)

# Buttons
button_frame = tk.Frame(root, bg="#F2F5F9")
button_frame.pack()

tk.Button(
    button_frame,
    text="Calculate BMI",
    command=calculate_bmi,
    font=("Arial", 10, "bold"),
    bg="#2563EB",
    fg="white",
    activebackground="#1D4ED8",
    activeforeground="white",
    relief="flat",
    padx=18,
    pady=9,
    cursor="hand2"
).pack(side="left", padx=6)

tk.Button(
    button_frame,
    text="Reset",
    command=reset_fields,
    font=("Arial", 10, "bold"),
    bg="#64748B",
    fg="white",
    activebackground="#475569",
    activeforeground="white",
    relief="flat",
    padx=18,
    pady=9,
    cursor="hand2"
).pack(side="left", padx=6)

# Disclaimer
tk.Label(
    root,
    text="BMI is a screening measure, not a medical diagnosis.",
    font=("Arial", 8),
    bg="#F2F5F9",
    fg="#687386"
).pack(side="bottom", pady=12)

root.mainloop()
