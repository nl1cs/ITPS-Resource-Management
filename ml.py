import spacy
import pandas as pd
import re

from collections import defaultdict
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
fp = open('data/sample.pdf', 'rb')
rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
pages = PDFPage.get_pages(fp)
connected_text = ""
for page in pages:
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
    questions.append(question)
# Read the CSV file into a DataFrame
df = pd.read_csv('data/questions.csv')

# Initialize a defaultdict to store the data
train_dataset = defaultdict(list)

# Iterate through the DataFrame and populate the dictionary
for index, row in df.iterrows():
    # Iterate through subject columns (subjects.0, subjects.1, subjects.2, subjects.3)
    for col in df.columns[df.columns.str.startswith('subjects.')]:
        subject = row[col]
        if pd.notna(subject):
            # Clean and format the subject
            subject = subject.strip().capitalize()
            train_dataset[subject].append(row['title'])

    # Iterate through skill columns (skills.0, skills.1, skills.2)
    for col in df.columns[df.columns.str.startswith('skills.')]:
        skill = row[col]
        if pd.notna(skill):
            # Clean and format the skill
            skill = skill.strip().capitalize()
            train_dataset[skill].append(row['title'])

# Convert the defaultdict to a regular dictionary
data = dict(train_dataset)


# see github repo for examples on sentence-transformers and Huggingface
nlp = spacy.load('en_core_web_md')
nlp.add_pipe("classy_classification", 
    config={
        "data": data,
        "model": "spacy"
    }
)

nlp_ner = spacy.load("model-best")

for question in questions:
    title = question['title']
    doc = nlp_ner(title)

    # Sort the categories by their scores in descending order
    sorted_categories = sorted(doc._.cats.items(), key=lambda x: x[1], reverse=True)

    print(f"Title: {title}")
    print("Top 3 Classification Scores:")

    # Print the top 3 categories and scores
    for category, score in sorted_categories[:3]:
        print(f"{category}: {score}")