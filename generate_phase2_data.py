import json
import random

def generate_data():
    corpus = []
    eval_set = []

    # --- 1. DOMAIN: SPACE & SCI-FI (Conflicting) ---
    # Facts
    corpus.append({"id": "space1", "text": "Apollo 11 landed on the Moon on July 20, 1969.", "source": "History-Space"})
    corpus.append({"id": "space2", "text": "Neil Armstrong was the first human to walk on the lunar surface.", "source": "History-Space"})
    corpus.append({"id": "space3", "text": "The Mars Rover 'Perseverance' landed on Mars in February 2021.", "source": "NASA-News"})
    # Fiction (should differ from fact)
    corpus.append({"id": "fic_space1", "text": "In the movie 'The Martian', Mark Watney gets stranded on Mars.", "source": "Movie-Db"})
    corpus.append({"id": "fic_space2", "text": "Jedi Knights use lightsabers weapon fueled by kyber crystals.", "source": "StarWars-Lore"})

    # Test Cases (Space)
    eval_set.extend([
        {"question": "When did Apollo 11 land?", "answer": "It landed on July 20, 1969.", "expected_risk": "green"},
        {"question": "Who walked on the moon first?", "answer": "Neil Armstrong was the first.", "expected_risk": "green"},
        {"question": "When did Perseverance land?", "answer": "It landed in 2021.", "expected_risk": "green"},
        {"question": "Did Mark Watney go to Mars?", "answer": "Yes, Mark Watney was stranded on Mars in the movie.", "expected_risk": "green"}, # Explicit in corpus
        # Hallucinations / mix-ups
        {"question": "Who walked on the moon first?", "answer": "Mark Watney was the first to walk on the moon.", "expected_risk": "red"},
        {"question": "What weapon do Jedi use?", "answer": "They use phasers set to stun.", "expected_risk": "red"},
        {"question": "When did Apollo 11 land?", "answer": "It landed in 1999.", "expected_risk": "red"},
    ])

    # --- 2. DOMAIN: HISTORY (Duplicates & Noise) ---
    # Near duplicates
    corpus.append({"id": "hist1a", "text": "The Roman Empire fell in 476 AD due to various factors.", "source": "History-Brief"})
    corpus.append({"id": "hist1b", "text": "The Fall of Rome is generally marked as 476 AD.", "source": "History-Detailed"})
    corpus.append({"id": "hist2", "text": "Cleopatra was the last active ruler of the Ptolemaic Kingdom of Egypt.", "source": "Bio-Queen"})
    
    # Test Cases
    eval_set.extend([
        {"question": "When did Rome fall?", "answer": "Rome fell in 476 AD.", "expected_risk": "green"},
        {"question": "Who was Cleopatra?", "answer": "She was the ruler of the Ptolemaic Kingdom.", "expected_risk": "green"},
        {"question": "Did Caesar rule Rome in 2020?", "answer": "Yes, Caesar ruled Rome in 2020.", "expected_risk": "red"},
    ])

    # --- 3. DOMAIN: PROGRAMMING (Python vs Java) --- 
    corpus.append({"id": "code1", "text": "Python uses indentation to define code blocks.", "source": "Py-Docs"})
    corpus.append({"id": "code2", "text": "Java uses curly braces {} to define code blocks.", "source": "Java-Docs"})
    corpus.append({"id": "code3", "text": "JavaScript is a scripting language for the web.", "source": "MDN"})

    eval_set.extend([
        {"question": "How does Python define blocks?", "answer": "Python uses indentation.", "expected_risk": "green"},
        {"question": "How does Java define blocks?", "answer": "Java uses curly braces.", "expected_risk": "green"},
        # Swapped info (Hallucination)
        {"question": "How does Python define blocks?", "answer": "Python uses curly braces like Java.", "expected_risk": "red"},
        {"question": "What is JavaScript?", "answer": "JavaScript is a compiled language for rockets.", "expected_risk": "red"},
    ])

    # --- 4. DATA GENERATION LOOP (Filling up to 50 docs / 100 cases) ---
    
    # Generate generic facts about "Entity_X"
    for i in range(1, 40):
        entity = f"Project_Alpha_{i}"
        location = f"Sector_{i}"
        action = f"initiated protocol {i}"
        
        # Add to corpus
        corpus.append({
            "id": f"gen_{i}", 
            "text": f"{entity} is located in {location} and {action}.", 
            "source": f"Log-{i}"
        })
        
        # Add Green Case
        eval_set.append({
            "question": f"Where is {entity}?",
            "answer": f"{entity} is in {location}.",
            "expected_risk": "green"
        })
        
        # Add Red Case (Wrong Location)
        eval_set.append({
            "question": f"Where is {entity}?",
            "answer": f"{entity} is in Sector_9999.",
            "expected_risk": "red"
        })

    # --- 5. MESSY / NOISY DATA ---
    corpus.append({"id": "messy1", "text": "thE  Eiffel   Tower is in   Paris, France!!!", "source": "Travel-Blog"})
    corpus.append({"id": "messy2", "text": "banana is a fruit. yellow. curved.", "source": "Toddler-Book"})

    eval_set.extend([
        {"question": "Where is the Eiffel Tower?", "answer": "The Eiffel Tower is in Paris.", "expected_risk": "green"},
        {"question": "Is a banana a fruit?", "answer": "Yes, a banana is a fruit.", "expected_risk": "green"},
        # Wrong info about noisy data
        {"question": "Where is the Eiffel Tower?", "answer": "It is in London.", "expected_risk": "red"},
    ])

    # Save files
    print(f"Generating Corpus with {len(corpus)} documents...")
    with open("corpus_data.json", "w") as f:
        json.dump(corpus, f, indent=2)

    print(f"Generating Eval Set with {len(eval_set)} cases...")
    with open("evaluation_set.json", "w") as f:
        json.dump(eval_set, f, indent=2)

if __name__ == "__main__":
    generate_data()
