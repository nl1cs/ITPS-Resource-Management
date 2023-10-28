from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re
import csv
import spacy
import spacy_setfit
fp = open('data/sample.pdf', 'rb')
rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
pages = PDFPage.get_pages(fp)
connected_text = ""
for page in pages:
    print('Processing next page...')
    interpreter.process_page(page)
    layout = device.get_result()

    # Round the bounding box coordinates to 35, 39, and 42
    rounded_layout = [lobj for lobj in layout]
    for lobj in rounded_layout:
        lobj.bbox = (
            35 if lobj.bbox[0] < 35 else 42 if lobj.bbox[0] > 42 else round(lobj.bbox[0], 2),
            lobj.bbox[1],
            35 if lobj.bbox[2] < 35 else 42 if lobj.bbox[2] > 42 else round(lobj.bbox[2], 2),
            lobj.bbox[3]
        )

    # Remove layout objects with specified rounded coordinates
    filtered_layout = [lobj for lobj in layout if lobj.bbox[3] > 50]


    # Create an empty string to store the connected text


    for lobj in filtered_layout:
        if isinstance(lobj, LTTextBox):
            # print(lobj.bbox, lobj)
            connected_text += lobj.get_text()

    # Print the connected text
lines = connected_text.split('\n')

pattern1 = r'\.\n+'

# Remove the pattern from the text
cleaned_text = re.sub(pattern1, '', connected_text)
pattern = r'(\d+)\s+([\s\S]+?)(?:[A-D]\)\s*([\s\S]+?)(?=(?:[A-D]\))|(?=\d|$)))+'
# print(cleaned_text)
# Find all matches in the text
matches = re.finditer(pattern, cleaned_text)

# Initialize variables to store questions
questions = []

# Iterate through the matches and extract titles and options
for match in matches:
    number = match.group(1)
    title = re.sub(r'(?<!\. )\n', '', match.group(2).strip())
    option_matches = re.finditer(r'([A-D]\))\s*([\s\S]+?)(?=(?:[A-D]\))|(?=\d|$))', match.group())
    options = {f"options.{i}.option": match.group(2).strip() for i, match in enumerate(option_matches)}

    question = {
        "title": title,
        "options": options
    }
    # print(question)
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

# Your existing code for extracting questions from the PDF

# Iterate through questions and print titles
for question in questions:
    title = question['title']
    print(title)



