import spacy
nlp = spacy.load('textcat_model/model-best')
doc = nlp("How rocks and their chemistry change with each successive layer is important. As the oceanic slab descends, magma begins rising up and erupts on the surface in layers atop one another, creating a rising sequence of igneous rocks. With increasing depth, heat and pressure begin squeezing different elements out of the slab in fluids. Over time, these fluids change the chemical composition of the lavas so that they become rich in rare earth elements like ytterbium, but poor in the element niobium. The first layer in the sequence erupts before the fluids can escape the slab, but the next layer in the sequence gets just enough fluid to make a partial signature. The final layer carries huge amounts of rare earth elements and very little niobium, together making the clarion mark of subduction zone lava. Which choice best states the main idea of the text?")

# Sort the doc.cats dictionary by values in descending order
sorted_categories = sorted(doc.cats.items(), key=lambda x: x[1], reverse=True)

# Get the top three categories
top_three_categories = sorted_categories[:3]

# Print the top three categories and their scores
for category, score in sorted_categories:
    print(f'{category}')
