import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import PyPDF2
# Load your DialogRPT model
model_name = "microsoft/DialogRPT-updown"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Read the CSV file containing titles and options
csv_file = 'data/questions.csv'
df = pd.read_csv(csv_file)

# Preprocess the text from the CSV
titles = df['title'].tolist()
options = df[['options.0.option', 'options.1.option', 'options.2.option', 'options.3.option']].values.tolist()

# Combine the titles and options
text_data = []
for title, option_set in zip(titles, options):
    text_data.append(title)
    text_data.extend(option_set)

# Extract text from the PDF
pdf_file = 'data/sample.pdf'
pdf_text = ""
with open(pdf_file, 'rb') as pdfFileObj:
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    for page in pdfReader.pages:
        pdf_text += page.extract_text()
# Tokenize and classify
inputs = tokenizer(pdf_text, return_tensors="pt", padding=True, truncation=True)

with torch.no_grad():
    logits = model(**inputs).logits

# Thresholding for class prediction
threshold = 0.5
predicted_class_ids = torch.arange(logits.shape[-1])[torch.sigmoid(logits) > threshold]

# Define a dictionary to map class ids to labels
class_id_to_label = {i: model.config.id2label[i] for i in predicted_class_ids}

# Initialize variables to store parts of the PDF
title = ""
options = []

# Classify parts based on class labels
for i, label_id in enumerate(predicted_class_ids):
    label = class_id_to_label[label_id]
    part = text_data[i]

    if label == "title":
        title += part
    elif label == "option":
        options.append(part)

# Print the classified parts
print("Title:", title)
print("Options:")
for option in options:
    print(option)
