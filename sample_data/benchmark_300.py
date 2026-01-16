"""
Benchmark 300: The "Messy & Confusing" Extension.
Adds 100 items designed to break models with noise, ambiguity, and complex linguistics.
"""

from sample_data.benchmark_200 import BENCHMARK_200 as PREV_200

MESSY_100 = [
    # --- TYPOS & NOISY TEXT (20) ---
    {"claim": "The product cost $50.", "evidence": "The prodcut cots $50.", "expected": "ENTAILED"}, # Simple typos
    {"claim": "Meeting is cancelled.", "evidence": "Mtg is cnxld.", "expected": "ENTAILED"}, # Abbr
    {"claim": "He is happy.", "evidence": "He is hapy.", "expected": "ENTAILED"},
    {"claim": "System is offline.", "evidence": "System status: 0ffline (typ0).", "expected": "ENTAILED"},
    {"claim": "The car is red.", "evidence": "The car is rad.", "expected": "NEUTRAL"}, # Rad = cool != red
    {"claim": "Vote for Pedro.", "evidence": "V0te f0r P3dr0.", "expected": "ENTAILED"}, # Leet speak
    {"claim": "She accepted the job.", "evidence": "She except the job.", "expected": "ENTAILED"}, # Common grammar error, but semantic intent often implied? Or Contradiction? Usually NLI treats this as Entailment if meaning is clear.
    {"claim": "I want a dessert.", "evidence": "I want a desert.", "expected": "NEUTRAL"}, # Dessert vs Desert
    {"claim": "Its a good day.", "evidence": "It's a good day.", "expected": "ENTAILED"}, # Its vs It's
    {"claim": "The effect was small.", "evidence": "The affect was small.", "expected": "ENTAILED"}, # Effect vs Affect
    {"claim": "Total is 100.", "evidence": "Toatl is 1 0 0.", "expected": "ENTAILED"}, # Spacing
    {"claim": "File not found.", "evidence": "Error 404: File Not Found.", "expected": "ENTAILED"},
    {"claim": "Access denied.", "evidence": "Success: Access Granted.", "expected": "CONTRADICTED"},
    {"claim": "He read the book.", "evidence": "He red the book.", "expected": "ENTAILED"}, # Phonetic typo
    {"claim": "No smoking.", "evidence": "Non-smoking area.", "expected": "ENTAILED"},
    {"claim": "Allowed here.", "evidence": "Aloud here.", "expected": "NEUTRAL"}, # Allowed vs Aloud
    {"claim": "Buy the bread.", "evidence": "By the bread.", "expected": "NEUTRAL"}, # Buy vs By
    {"claim": "The site is live.", "evidence": "The site is <live>.", "expected": "ENTAILED"},
    {"claim": "Data is clean.", "evidence": "Data is cl3an.", "expected": "ENTAILED"},
    {"claim": "Go to the sea.", "evidence": "Go to the see.", "expected": "NEUTRAL"},

    # --- IDIOMS & SLANG (20) ---
    {"claim": "It was expensive.", "evidence": "It cost an arm and a leg.", "expected": "ENTAILED"},
    {"claim": "Currently raining.", "evidence": "It's raining cats and dogs.", "expected": "ENTAILED"},
    {"claim": "He is dead.", "evidence": "He kicked the bucket.", "expected": "ENTAILED"},
    {"claim": "She is ignored.", "evidence": "She was given the cold shoulder.", "expected": "ENTAILED"},
    {"claim": "It was easy.", "evidence": "It was a piece of cake.", "expected": "ENTAILED"},
    {"claim": "Wait a moment.", "evidence": "Hold your horses.", "expected": "ENTAILED"},
    {"claim": "He is very happy.", "evidence": "He is over the moon.", "expected": "ENTAILED"},
    {"claim": "I am listening.", "evidence": "I'm all ears.", "expected": "ENTAILED"},
    {"claim": "Good luck.", "evidence": "Break a leg.", "expected": "ENTAILED"},
    {"claim": "It is rare.", "evidence": "It happens once in a blue moon.", "expected": "ENTAILED"},
    {"claim": "He revealed the secret.", "evidence": "He spilled the beans.", "expected": "ENTAILED"},
    {"claim": "She is sick.", "evidence": "She is under the weather.", "expected": "ENTAILED"},
    {"claim": "Stop working.", "evidence": "Call it a day.", "expected": "ENTAILED"},
    {"claim": "He is crazy.", "evidence": "He has a screw loose.", "expected": "ENTAILED"},
    {"claim": "The car is broken.", "evidence": "The car is a lemon.", "expected": "ENTAILED"},
    {"claim": "I have no money.", "evidence": "I'm broke.", "expected": "ENTAILED"},
    {"claim": "It's cool.", "evidence": "It's lit.", "expected": "ENTAILED"}, # Gen Z slang
    {"claim": "That looks fake.", "evidence": "That looks sus.", "expected": "ENTAILED"},
    {"claim": "He is bragging.", "evidence": "He is flexing.", "expected": "ENTAILED"},
    {"claim": "She is lying.", "evidence": "She is capping.", "expected": "ENTAILED"},

    # --- LOGICAL TRAPS & DOUBLE NEGATIVES (20) ---
    {"claim": "I went there.", "evidence": "I didn't say I never went there.", "expected": "ENTAILED"}, # Technically maybe neutral, but often implies yes.
    {"claim": "It is not uncommon.", "evidence": "It is common.", "expected": "ENTAILED"},
    {"claim": "He is not unhappy.", "evidence": "He is happy.", "expected": "ENTAILED"}, # Litotes
    {"claim": "Nobody is absent.", "evidence": "Everyone is present.", "expected": "ENTAILED"},
    {"claim": "Don't not go.", "evidence": "Go.", "expected": "ENTAILED"},
    {"claim": "It is not impossible.", "evidence": "It is possible.", "expected": "ENTAILED"},
    {"claim": "I doubt he didn't do it.", "evidence": "I think he did it.", "expected": "ENTAILED"},
    {"claim": "The door is not closed.", "evidence": "The door is open.", "expected": "ENTAILED"},
    {"claim": "The light is off.", "evidence": "The light is not on.", "expected": "ENTAILED"},
    {"claim": "He is not incorrect.", "evidence": "He is right.", "expected": "ENTAILED"},
    {"claim": "Everything is false.", "evidence": "Nothing is true.", "expected": "ENTAILED"},
    {"claim": "The glass is half empty.", "evidence": "The glass is half full.", "expected": "ENTAILED"}, # Physically equivalent
    {"claim": "A implies B.", "evidence": "If A then B.", "expected": "ENTAILED"},
    {"claim": "A implies B.", "evidence": "B implies A.", "expected": "NEUTRAL"}, # Converse error
    {"claim": "He lacks nothing.", "evidence": "He has everything.", "expected": "ENTAILED"},
    {"claim": "It is arguably true.", "evidence": "It is definitely true.", "expected": "NEUTRAL"}, # Arguably != Definitely
    {"claim": "He barely made it.", "evidence": "He didn't make it.", "expected": "CONTRADICTED"},
    {"claim": "Usually yes.", "evidence": "Always yes.", "expected": "CONTRADICTED"}, # Usually != Always
    {"claim": "Almost all.", "evidence": "100%.", "expected": "CONTRADICTED"},
    {"claim": "Not bad.", "evidence": "Good.", "expected": "ENTAILED"},

    # --- POLYSEMY & AMBIGUITY (20) ---
    {"claim": "I saw the bat.", "evidence": "I saw the flying mammal.", "expected": "ENTAILED"}, # If context known... ambiguous
    {"claim": "I saw the bat.", "evidence": "I saw the baseball equipment.", "expected": "NEUTRAL"}, # Ambiguous
    {"claim": "The bank is wet.", "evidence": "The river bank is wet.", "expected": "ENTAILED"},
    {"claim": "The bank is wet.", "evidence": "The financial institution is wet.", "expected": "NEUTRAL"},
    {"claim": "I heard the bark.", "evidence": "I heard the tree skin.", "expected": "NEUTRAL"},
    {"claim": "I heard the bark.", "evidence": "I heard the dog sound.", "expected": "ENTAILED"},
    {"claim": "It is light.", "evidence": "It is not heavy.", "expected": "ENTAILED"},
    {"claim": "It is light.", "evidence": "It is bright.", "expected": "NEUTRAL"}, # Ambiguous
    {"claim": "The crane is tall.", "evidence": "The bird is tall.", "expected": "ENTAILED"},
    {"claim": "The crane is tall.", "evidence": "The construction machine is tall.", "expected": "NEUTRAL"}, 
    {"claim": "He plays bass.", "evidence": "He plays the fish.", "expected": "CONTRADICTED"},
    {"claim": "He plays bass.", "evidence": "He plays the guitar.", "expected": "ENTAILED"},
    {"claim": "She tears the paper.", "evidence": "She rips the paper.", "expected": "ENTAILED"},
    {"claim": "She has tears.", "evidence": "She is crying.", "expected": "ENTAILED"},
    {"claim": "Book a room.", "evidence": "Reserve a room.", "expected": "ENTAILED"},
    {"claim": "Read a book.", "evidence": "Consume literature.", "expected": "ENTAILED"},
    {"claim": "It is cool.", "evidence": "The temperature is low.", "expected": "ENTAILED"},
    {"claim": "It is cool.", "evidence": "It is fashionable.", "expected": "NEUTRAL"},
    {"claim": "Duck!", "evidence": "Lower your head!", "expected": "ENTAILED"},
    {"claim": "Duck!", "evidence": "A water bird!", "expected": "NEUTRAL"},

    # --- FORMATTING & TECHNICAL NOISE (20) ---
    {"claim": "Name: John.", "evidence": "{\"name\": \"John\"}", "expected": "ENTAILED"}, # JSON
    {"claim": "He is bold.", "evidence": "He is <b>bold</b>.", "expected": "ENTAILED"}, # HTML
    {"claim": "Price < 100.", "evidence": "Price is less than 100.", "expected": "ENTAILED"},
    {"claim": "A & B.", "evidence": "A and B.", "expected": "ENTAILED"},
    {"claim": "User_ID=5.", "evidence": "The User ID is 5.", "expected": "ENTAILED"},
    {"claim": "Select * From Users.", "evidence": "Select all users.", "expected": "ENTAILED"}, # SQL
    {"claim": "Print 'Hello'.", "evidence": "Output Hello.", "expected": "ENTAILED"},
    {"claim": "C:\\Docs\\File.txt", "evidence": "File is in Docs folder.", "expected": "ENTAILED"},
    {"claim": "https://site.com", "evidence": "The website URL.", "expected": "ENTAILED"},
    {"claim": "Error 500.", "evidence": "Internal Server Error.", "expected": "ENTAILED"},
    {"claim": "x = 5; y = 10;", "evidence": "x is 5 and y is 10.", "expected": "ENTAILED"},
    {"claim": "TODO: Fix bug.", "evidence": "There is a bug to fix.", "expected": "ENTAILED"},
    {"claim": "# Comment.", "evidence": "This is a comment.", "expected": "ENTAILED"},
    {"claim": "1. Option A\n2. Option B", "evidence": "Option A is first.", "expected": "ENTAILED"},
    {"claim": "Email: bob@mail.com", "evidence": "Bob's email is bob@mail.com.", "expected": "ENTAILED"},
    {"claim": "Log: [INFO] Started.", "evidence": "The system started.", "expected": "ENTAILED"},
    {"claim": "Status: OK.", "evidence": "Status: 200 OK.", "expected": "ENTAILED"},
    {"claim": "Ctrl+C", "evidence": "Copy command.", "expected": "ENTAILED"},
    {"claim": "404 Not Found", "evidence": "The page is missing.", "expected": "ENTAILED"},
    {"claim": "End of file.", "evidence": "EOF.", "expected": "ENTAILED"}
]

BENCHMARK_300 = PREV_200 + MESSY_100
