import pandas as pd
from collections import defaultdict
from spacy.tokens import DocBin
import spacy
nlp = spacy.blank("en")
db = DocBin()
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

# Convert the defaultdict to a regular dictionary
train_dataset = dict(train_dataset)

doc_bins = {}

db = DocBin()
categories = list(train_dataset.keys())

# Iterate through the categories and questions
for category, questions in train_dataset.items():
    for question in questions:
        doc = nlp.make_doc(question)
        doc.cats = {cat: 1 if cat == category else 0 for cat in categories}
        db.add(doc)

# Save the single DocBin to a binary file
db.to_disk("questions.spacy")

#python3 -m spacy init config --pipeline textcat_multilabel config.cfg
#python3 -m spacy train config.cfg --paths.train questions.spacy  --paths.dev ./questions.spacy --output textcat_model
