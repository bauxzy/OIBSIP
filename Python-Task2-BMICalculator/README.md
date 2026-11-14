BMI Calculator
A simple and beginner-friendly BMI (Body Mass Index) Calculator built with Python and Tkinter. The application allows users to enter their weight and height, calculate their BMI, and view the corresponding adult BMI category through a clean desktop interface.
Features
- Calculate BMI using weight in kilograms and height in centimeters.
- Display the calculated BMI rounded to two decimal places.
- Classify the result as Underweight, Normal weight, Overweight, or Obesity.
- Validate inputs and display an error message for invalid or non-positive values.
- Reset the input fields and result display.
- Simple graphical user interface built with Tkinter.
BMI Formula
The application uses the standard BMI formula:
\[
\text{BMI} = \frac{\text{Weight (kg)}}{\text{Height (m)}^2}
\]
Height is converted from centimeters to meters before the calculation.
BMI Categories
BMI range	Category
Below 18.5	Underweight
18.5 to below 25	Normal weight
25 to below 30	Overweight
30 or above	Obesity


These are general adult screening categories. BMI is not a medical diagnosis.
Technologies Used
- Python 3
- Tkinter — graphical user interface
- Standard Python library — input handling and calculations
Project Structure
Python-Task2-BMICalculator/
├── main.py
├── README.md
├── requirements.txt
└── screenshots/
    ├── 01-main-interface.png
    ├── 02-bmi-result.png
    └── 03-input-validation.png
Installation and Setup
1. Clone the repository
git clone https://github.com/bauxzy/OIBSIP.git
2. Open the project folder
cd OIBSIP/Python-Task2-BMICalculator
3. Run the application
python main.py
On some Windows systems, you can use:
py main.py
How to Use
1. Launch the application.
2. Enter your weight in kilograms.
3. Enter your height in centimeters.
4. Click Calculate BMI.
5. View your BMI value and category.
6. Click Reset to clear the fields and start again.
Screenshots
Add screenshots of the running application to the screenshots/ folder and keep the filenames shown below.
Main Interface

BMI Calculation Result

Input Validation

Dependencies
This project uses Python's standard library and does not require third-party packages. Tkinter must be available in your Python installation.
Internship Task
Program: Oasis Infobyte Internship
Task: Python Programming — Task 2
Project: BMI Calculator
Disclaimer
This application is intended for educational purposes. BMI is a screening measure and should not be used as a substitute for professional medical advice, diagnosis, or treatment.