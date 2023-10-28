import PyPDF2
import re
import csv

def crop_pdf_text(pdf_file, top, bottom):
    pdf_text = ""

    with open(pdf_file, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        for page in pdfReader.pages:
            # page.mediabox.lower_right = (612, 500)
            # page.mediabox.lower_left = (0, 120)
            # page.mediabox.upper_right = (612, 500)
            # page.mediabox.upper_left = (0, 711)
            page.mediabox.upper_right = (
            page.mediabox.right / 2,
            page.mediabox.top / 2,
)
            
            page_text = page.extract_text()
            pdf_text += page_text
            print(pdf_text)
            
    
pdf_file = 'data/sample.pdf'
top = 81
bottom = 63

# Crop the PDF text
cropped_text = crop_pdf_text(pdf_file, top, bottom)


pattern = r'(\d+)\s+([\s\S]+?)(?:[A-D]\)\s*([\s\S]+?)(?=(?:[A-D]\))|(?=\d|$)))+'

# Find all matches in the text
matches = re.finditer(pattern, cropped_text)

# Initialize variables to store questions
questions = []

# Iterate through the matches and extract titles and options
for match in matches:
    number = match.group(1)
    title = match.group(2).strip()
    option_matches = re.finditer(r'([A-D]\))\s*([\s\S]+?)(?=(?:[A-D]\))|(?=\d|$))', match.group())
    options = {f"options.{i}.option": match.group(2).strip() for i, match in enumerate(option_matches)}

    question = {
        "title": title,
        "options": options
    }
    questions.append(question)

# Define the structure of the CSV
csv_structure = [
    "title",
    "module",
    "isMulti",
    "subjects.0",
    "subjects.1",
    "subjects.2",
    "subjects.3",
    "skills.0",
    "skills.1",
    "skills.2",
    "test",
    "difficulty",
    "standardTime",
    "optionsType",
    "options.0.option",
    "options.1.option",
    "options.2.option",
    "options.3.option",
]

# Create and write to the CSV file
with open("output.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_structure)
    writer.writeheader()

    for i, question in enumerate(questions):
        data = {
            "title": question['title'],
            "module": "",  # Add your module value here
            "isMulti": "",  # Add your isMulti value here
            "subjects.0": "",  # Add your subjects values here
            "subjects.1": "",
            "subjects.2": "",
            "subjects.3": "",
            "skills.0": "",  # Add your skills values here
            "skills.1": "",
            "skills.2": "",
            "test": "",  # Add your test value here
            "difficulty": "",  # Add your difficulty value here
            "standardTime": "",  # Add your standardTime value here
            "optionsType": "",  # Add your optionsType value here
        }

        for key, value in question['options'].items():
            data[key] = value

        # Write data to the CSV file
        writer.writerow(data)

print("Data written to output.csv")
