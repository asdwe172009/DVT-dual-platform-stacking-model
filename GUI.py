from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import hashlib
import numpy as np
import joblib
import csv
import sys
import os
import warnings
warnings.filterwarnings("ignore")
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_credentials(username, password, filename):
    hashed_password = hash_password(password)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password])

def check_credentials(username, password, filename):
    hashed_password = hash_password(password)
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == hashed_password:
                return True
    return False

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Register")
        self.setWindowIcon(QIcon('red blood cell.png'))

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton("Register")

        self.register_button.clicked.connect(self.register)

        layout = QFormLayout()
        layout.addRow(self.username_label, self.username_input)
        layout.addRow(self.password_label, self.password_input)
        layout.addRow(self.register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        save_credentials(username, password, 'credentials.csv')

        QMessageBox.information(self, "Registration successful", "You can now log in with your new account.")
        self.close()

CSV_FILE = 'patient_data.csv'
class PatientInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patient Information Administration")
        self.setWindowIcon(QIcon('red blood cell.png'))
        self.setMinimumSize(800, 600)



        # Create the table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # For ID, Name, Biomarker1, Biomarker2, Biomarker3, Biomarker4
        self.table.setHorizontalHeaderLabels(
            ["Patient ID", "Name", "Biomarker1", "Biomarker2", "Biomarker3", "Biomarker4", "Biomarker5"])

        layout = QFormLayout(self)
        layout.addWidget(self.table)

        # Buttons for Add, Delete, Modify, Check
        self.add_button = QPushButton("Add Patient")
        self.delete_button = QPushButton("Delete Patient")
        self.modify_button = QPushButton("Modify Patient")
        self.save_changes_button = QPushButton("Save Changes")

        # Connect buttons to functions (implement these functions as needed)
        self.add_button.clicked.connect(self.add_patient)
        self.delete_button.clicked.connect(self.delete_patient)
        self.modify_button.clicked.connect(self.modify_patient)
        self.save_changes_button.clicked.connect(self.save_changes)

        # Add buttons to layout
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.modify_button)
        layout.addWidget(self.save_changes_button)

        self.patient_id_input = QLineEdit()
        self.patient_name_input = QLineEdit()
        self.biomarker1_input = QLineEdit()
        self.biomarker2_input = QLineEdit()
        self.biomarker3_input = QLineEdit()
        self.biomarker4_input = QLineEdit()
        self.biomarker5_input = QLineEdit()


        layout.addRow("Patient ID", self.patient_id_input)
        layout.addRow("Patient Name", self.patient_name_input)
        layout.addRow("Biomarker 1", self.biomarker1_input)
        layout.addRow("Biomarker 2", self.biomarker2_input)
        layout.addRow("Biomarker 3", self.biomarker3_input)
        layout.addRow("Biomarker 4", self.biomarker4_input)
        layout.addRow("Biomarker 5", self.biomarker5_input)
        # Load the machine learning model
        self.model = joblib.load("sclf-SHAP screen metabolites.pkl")

        # Set up a text output section for the model prediction
        self.prediction_output = QLabel("Prediction result will be shown here.")
        layout.addWidget(self.prediction_output)

        # Connect row selection signal to prediction method
        self.table.itemSelectionChanged.connect(self.make_prediction)

        self.setLayout(layout)
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.showMaximized()
    def load_data(self):
        """ Load patient data from the CSV file and display in the table. """
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Patient ID", "Name", "Biomarker1", "Biomarker2", "Biomarker3", "Biomarker4","Biomarker5"])

        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                self.add_row_to_table(row)

    def add_row_to_table(self, row_data):
        """ Add a row to the table with the provided data. """
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, data in enumerate(row_data):
            item = QTableWidgetItem(data)
            self.table.setItem(row, i, item)
    # Implement the functionalities for each button
    def add_patient(self):
        """ Add a new patient to the CSV file and the table. """
        # Collect data from input fields or a form
        # Example: patient_data = [self.patient_id_input.text(), self.patient_name_input.text(), ...]
        patient_data = [self.patient_id_input.text(),
                        self.patient_name_input.text(),
                        self.biomarker1_input.text(),
                        self.biomarker2_input.text(),
                        self.biomarker3_input.text(),
                        self.biomarker4_input.text(),
                        self.biomarker5_input.text()]
        # Check for empty fields
        if any(not field.strip() for field in patient_data):
            QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
            return

        # Check for duplicate Patient ID
        if self.is_duplicate_patient_id(patient_data[0]):
            QMessageBox.warning(self, "Duplicate Entry", "A patient with this ID already exists.")
            return

        # Add data to the table
        self.add_row_to_table(patient_data)

        # Append data to CSV file
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(patient_data)

        # Add data to the table
        self.add_row_to_table(patient_data)
        self.refresh_table()

    def is_duplicate_patient_id(self, patient_id):
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == patient_id:
                    return True
        return False
    def delete_patient(self):
        """ Delete the selected patient from the CSV file and the table. """
        # Get selected row
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            patient_id = self.table.item(selected_row, 0).text()  # Assuming first column is Patient ID

            # Remove row from table
            self.table.removeRow(selected_row)

            # Remove data from CSV file
            # This requires reading all data, filtering out the deleted row, and rewriting the file
            new_data = []
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] != patient_id:
                        new_data.append(row)

            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(new_data)
    def modify_patient(self):
        # Code to modify existing patient info
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            # Assume first column is Patient ID
            patient_id = self.table.item(selected_row, 0).text()

            # Retrieve data and populate input fields
            # Assuming input fields are defined in __init__ for editing
            self.patient_id_input.setText(patient_id)
            self.patient_name_input.setText(self.table.item(selected_row, 1).text())
            self.biomarker1_input.setText(self.table.item(selected_row, 2).text())
            self.biomarker2_input.setText(self.table.item(selected_row, 3).text())
            self.biomarker3_input.setText(self.table.item(selected_row, 4).text())
            self.biomarker4_input.setText(self.table.item(selected_row, 5).text())
            self.biomarker5_input.setText(self.table.item(selected_row, 6).text())
            # ... set other fields ...

            # Add a Save Changes button and connect it to a new method to save changes
            self.save_changes_button = QPushButton("Save Changes")
            self.save_changes_button.clicked.connect(self.save_changes)
            # Add this button to your layout

    def save_changes(self):
        # Collect updated data from input fields
        updated_data = [
            self.patient_id_input.text(),
            self.patient_name_input.text(),
            self.biomarker1_input.text(),
            self.biomarker2_input.text(),
            self.biomarker3_input.text(),
            self.biomarker4_input.text(),
            self.biomarker5_input.text()
            # ... collect other fields ...
        ]
        # Update the data in the table
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            for col, data in enumerate(updated_data):
                self.table.setItem(selected_row, col, QTableWidgetItem(data))
        # Update the data in the CSV file
        self.update_csv_file()

    def update_csv_file(self):
        # Read all data from the table and write it to the CSV file
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in range(self.table.rowCount()):
                row_data = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
                writer.writerow(row_data)



    def refresh_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.load_data()

    def make_prediction(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            try:
                # Extract biomarker values
                biomarkers = [float(self.table.item(selected_row, col).text()) for col in
                              range(2, 7)]  # Assuming columns 2-5 are biomarkers
                # Reshape data for prediction
                data_to_predict = np.array([biomarkers])
                # Make prediction
                prediction = self.model.predict(data_to_predict)
                prob= self.model.predict_proba(data_to_predict)
                # Update the prediction output
                if prediction[0] == 0:
                    self.prediction_output.setText(f"Prediction: After prediction, the patient is classified into the non-DVT group.")
                else:
                    self.prediction_output.setText(f"Prediction: After prediction, the patient is classified into the DVT group with a probaility of {round((prob[0][1]*100),2)}%")
            except Exception as e:
                self.prediction_output.setText("Error in prediction: " + str(e))



class CombinedWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DVT Diagnosis and Classification System")
        self.resize(800, 600)  # Set the window size
        self.setWindowIcon(QIcon('red blood cell.png'))
        # Create the tab widget
        tab_widget = QTabWidget()

        # Create instances of the patient info and ML model windows
        patient_info_tab = PatientInfoWindow()
        # ml_model_tab = MLModelWindow()

        # Add tabs
        tab_widget.addTab(patient_info_tab, "Patient Information Management")
        # tab_widget.addTab(ml_model_tab, "Machine Learning Classification Model")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DVT Diagnosis System Login")
        self.setWindowIcon(QIcon('red blood cell.png'))
        # Set background image
        self.setAutoFillBackground(True)
        palette = self.palette()
        pixmap = QPixmap('background.jpg')  # Path to your background image
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        self.resize(800, 600)
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_credentials)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)


        main_layout = QVBoxLayout()
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label,self.username_input)
        form_layout.addRow(self.password_label,self.password_input)
        main_layout.addLayout(form_layout)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.quit_button)
        main_layout.addLayout(button_layout)


        self.setLayout(main_layout)

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if check_credentials(username, password, 'credentials.csv'):
            self.combined_window = CombinedWindow()
            self.combined_window.show()
            self.close()  # Optionally close the login window
        else:
            QMessageBox.warning(self, "Login error", "Incorrect username or password.")

    def register(self):
        self.register_window = RegisterWindow()
        self.register_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())

