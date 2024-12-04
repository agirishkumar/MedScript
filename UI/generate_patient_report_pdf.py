import json
from fpdf import FPDF

class PatientReportPDF(FPDF):
    def header(self):
        # Add a title
        self.set_font('Times', 'B', 16)
        self.cell(0, 10, 'Patient report', border=False, ln=1, align='C')
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y()) 
        self.ln(5)

    def footer(self):
        # Add a footer with page number
        self.set_y(-15)
        self.set_font('Times', 'I', 10)
        self.cell(0, 10, f'{self.page_no()}', align='C')
    
    def draw_patient_id(self, value):
        # Write the patient ID
        self.set_font("Times", "I", 12)
        self.cell(0, 10, f"Patient ID: {value}", 0, 1)
        self.ln(5)

    def draw_patient_record(self, value):
        # Write the patient record
        self.set_font("Times", "B", 12)
        self.cell(0, 10, "Patient Record", 0, 1)
        self.ln(2)

        self.set_font("Times", "", 10)
        for record_key, record_value in value.items():
            self.multi_cell(0, 8, u"{0}: {1}".format(record_key, record_value))
        self.ln(5)

    def draw_possible_diagnosis(self, value):
        # Write possible diagnosis
        self.set_font("Times", "B", 11)
        self.cell(0, 8, "Possible Diagnosis:", 0, 1)
        
        # Write primary diagnosis
        self.set_font("Times", "B", 10)
        self.cell(0, 8, "Primary Diagnosis:", 0, 1)
        self.set_font("Times", "", 10)
        self.multi_cell(0, 8, "- {0}".format(value['Primary Diagnosis']))

        # Write Differential Diagnosis
        self.set_font("Times", "B", 11)
        self.cell(0,8,"Differential Diagnosis", 0, 1)
        self.set_font("Times", "", 10)

        # Loop through the list and write to pdf
        for index, item in enumerate(value['Differential Diagnoses']):
            self.cell(5)
            self.multi_cell(0, 10, f"{index}. {item}")

    def draw_diagnosis_report(self, value):
        # Write diagnosis report
        self.set_font("Times", "B", 12)
        self.cell(0, 10, "Diagnosis Report", 0, 1)
        self.ln(2)

        self.set_font("Times", "", 10)
        for report_key, report_value in value.items():
            # Write the possible diagnosis
            if report_key == 'Possible Diagnoses':
                self.draw_possible_diagnosis(report_value)
                
            # Write all other elements in the possible diagnosis
            else:
                self.set_font("Times", "B", 10)
                self.cell(0, 8, report_key, 0, 1)
                self.set_font("Times", "", 10)

                self.multi_cell(0, 8, f"{report_value}".encode().decode('unicode-escape'))
            self.ln(3)

def create_pdf():
    # Create an instance of the PDF class
    pdf = PatientReportPDF()
    pdf.add_page()

    # Set font and add some content
    # pdf.set_font('Times', '', 12)
    # pdf.multi_cell(0, 10, "This is a sample PDF generated using Python and the FPDF library. "
    #                       "You can add multiple lines of text, and the text will automatically wrap.")
    
    with open('../models/test_records_with_med42.json') as file:
        data = json.load(file)[1]
        
        pdf.draw_patient_id(data['patientId'])

        pdf.draw_patient_record(data['patientRecord'])

        pdf.draw_diagnosis_report(data['diagnosisReport'])

        print(f"Report created succesfully.")

    return pdf.output(dest="S").encode("latin1")
