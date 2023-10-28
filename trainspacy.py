import spacy
from collections import defaultdict
import pandas as pd
import re
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans

nlp = spacy.blank('en')
df = pd.read_csv('data/questions.csv')

train_dataset = []

# Iterate through the DataFrame and populate the training dataset
for index, row in df.iterrows():
    for col in df.columns[df.columns.str.startswith('subjects.')]:
        subject = row[col]
        if pd.notna(subject):
            subject = subject.strip().capitalize()
            train_dataset.append({'text': row['title'], 'entities': []})
    
    for col in df.columns[df.columns.str.startswith('skills.')]:
        skill = row[col]
        if pd.notna(skill):
            skill = skill.strip().capitalize()
            train_dataset.append({'text': row['title'], 'entities': []})

doc_bin = DocBin()
for training_example in tqdm(train_dataset):
    text = training_example['text']
    labels = training_example['entities']
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in labels:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    filtered_ents = filter_spans(ents)
    doc.ents = filtered_ents
    doc_bin.add(doc)

doc_bin.to_disk("train.spacy")
