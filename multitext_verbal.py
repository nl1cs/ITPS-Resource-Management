import pandas as pd
from collections import defaultdict
from spacy.tokens import DocBin
import spacy
from sklearn.model_selection import train_test_split

nlp = spacy.blank("en")
db = DocBin()


# Read the data from the CSV file
df = pd.read_csv('data/questions.csv')

# Initialize defaultdicts to store the data
train_dataset = defaultdict(list)
train_dataset_verbal = defaultdict(list)

# Subjects related to math
math_subjects = [
    "Geometry",
    "System of equation",
    "Circle equation",
    "Heart of algebra",
    "Linear equation",
    "Quadratic equation",
    "Probability",
    "Graph",
    "Linear model",
    "Quadratic equation graph",
    "Table",
    "Radian",
    "Circle",
    "Conversion",
    "Tables",
    "Linear models",
    "Quadratic models",
    "System of equation model",
    "Triangle",
    "Angles",
    "Statistics",
    "Functions",
    "Min max value",
    "Exponential and linear functions",
    "Percentage",
    "Volume",
    "3d geometry",
    "Forms of functions",
    "Algebra",
    "Advanced math",
    "Geometry and trigonometry",
    "Word problem"

]

# Iterate through the DataFrame and populate the dictionaries
for index, row in df.iterrows():
    # Iterate through subject columns (subjects.0, subjects.1, subjects.2, subjects.3)
    for col in df.columns[df.columns.str.startswith('subjects.')]:
        subject = row[col]
        if pd.notna(subject):
            # Clean and format the subject
            subject = subject.strip().capitalize()
            
            # Check if the subject is related to math
            if subject in math_subjects:
                train_dataset[subject].append(row['title'])
            else:
                train_dataset_verbal[subject].append(row['title'])

# Convert the defaultdict to a regular dictionary
train_dataset = dict(train_dataset_verbal)
print(train_dataset)
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

#-m spacy train config.cfg --paths.train questions.spacy  --paths.dev questions.spacy --output textcat_model
titles = []
subjects = []

for subject, titles in train_dataset.items():
    for title in titles:
        titles.append(title)
        subjects.append(subject)

print(titles, subjects)
train_titles, test_titles, train_subjects, test_subjects = train_test_split(titles, subjects, train_size=0.8, random_state=13)

textcat = nlp.add_pipe("textcat_multilabel")
for i in subjects:
    textcat.add_label(i)

optimizer = nlp.begin_training()
iterations = 2
from spacy.util import minibatch, compounding
from spacy.training import Example

train_data = []
for feature, label in zip(train_titles, train_subjects):
    example = (feature, {"cats": {label: 1}})
    train_data.append(example)
with nlp.select_pipes(enable="textcat_multilabel"):
    for j in range(iterations):
        losses = {}
        k = 0
        batches = minibatch(train_data, size = compounding(4.,32.,1.001))
        for batch in batches:
            text, annotations = zip(*batch)
            example = []
            for i in range(len(text)):
                doc = nlp.make_doc(text[i])
                example.append(Example.from_dict(doc, annotations[i]))
            nlp.update(example, sgd=optimizer, drop=0.2, losses = losses)
            print('Batch No: {} Loss = {}'.format(k, round(losses['textcat_multilabel'])))
            k += 1
        print("\n\n Completed Iterations : {} ".format(j))

nlp.to_disk('models/')