"""
Massive 200-Item Benchmark for Hallucination Detection.
Includes:
1-100: Previous mixed items (General, Science, Logic)
101-120: Entity Precision (Fake Dates, Invented Numbers) -> Testing Logic v5
121-140: Legal Contracts (Strict wording)
141-160: Medical Reports (Dosages, Diagnoses)
161-180: News & Events (Names, Places, Actions)
181-200: Technical Specifications (Versions, Compatibility)
"""

from sample_data.benchmark_100 import BENCHMARK_100 as PREV_100

NEW_100 = [
    # --- ENTITY PRECISION / HALLUCINATION (20) ---
    # Testing the new date/number regex check
    {"claim": "The meeting happened on October 15th.", "evidence": "The meeting took place in mid-October.", "expected": "NEUTRAL"}, # Date specific vs vague
    {"claim": "Profit was exactly $10.5 million.", "evidence": "Profit was around $10 million.", "expected": "NEUTRAL"},
    {"claim": "Release date is January 1st, 2025.", "evidence": "Scheduled for release in Q1 2025.", "expected": "NEUTRAL"},
    {"claim": "Version 2.0 launched on Friday.", "evidence": "Version 2.0 launched last week.", "expected": "NEUTRAL"},
    {"claim": "Reference number is 12345.", "evidence": "Reference number is 12346.", "expected": "CONTRADICTED"},
    {"claim": "Report filed on July 4th.", "evidence": "Report filed on Independence Day.", "expected": "ENTAILED"}, # Tricky: Semantic knowledge needed
    {"claim": "Cost is $99.99.", "evidence": "The price is one hundred dollars.", "expected": "CONTRADICTED"}, # Cross-encoder might handle this, but strict nums might flag
    {"claim": "User ID is 500.", "evidence": "User ID is 500.", "expected": "ENTAILED"},
    {"claim": "Team size is 50 people.", "evidence": "The team consists of fifty individuals.", "expected": "ENTAILED"}, # Number word vs digit
    {"claim": "Established in 1990.", "evidence": "Founded in 1991.", "expected": "CONTRADICTED"},
    {"claim": "Incident occurring at 5:00 PM.", "evidence": "Incident happened in the late afternoon.", "expected": "NEUTRAL"},
    {"claim": "Invoice #900 paid.", "evidence": "Invoice #900 has been settled.", "expected": "ENTAILED"},
    {"claim": "Temperature reached 100 degrees.", "evidence": "It was very hot, reaching boiling point.", "expected": "ENTAILED"},
    {"claim": "Call duration 15 minutes.", "evidence": "Call lasted a quarter of an hour.", "expected": "ENTAILED"},
    {"claim": "CEO visited 5 cities.", "evidence": "The CEO visited London, Paris, and Tokyo.", "expected": "CONTRADICTED"}, # 3 != 5
    {"claim": "Score was 10-0.", "evidence": "It was a complete blowout victory.", "expected": "NEUTRAL"},
    {"claim": "Items count: 12.", "evidence": "There represent a dozen items.", "expected": "ENTAILED"},
    {"claim": "Born on May 5th.", "evidence": "Birthday is on Cinco de Mayo.", "expected": "ENTAILED"},
    {"claim": "Order 66 executed.", "evidence": "The command was given to execute Order 66.", "expected": "ENTAILED"},
    {"claim": "Refund amount $50.", "evidence": "Refund of $50 processed.", "expected": "ENTAILED"},

    # --- LEGAL CONTRACTS (20) ---
    {"claim": "Tenant must pay rent by the 1st.", "evidence": "Rent is due on the first day of each month.", "expected": "ENTAILED"},
    {"claim": "Landlord can enter anytime.", "evidence": "Landlord may enter with 24 hours notice.", "expected": "CONTRADICTED"},
    {"claim": "Pets are allowed.", "evidence": "No animals permitted on premises.", "expected": "CONTRADICTED"},
    {"claim": "Agreement terminates in 2025.", "evidence": "The lease ends on December 31, 2025.", "expected": "ENTAILED"},
    {"claim": "Late fee is 5%.", "evidence": "A late charge of five percent applies.", "expected": "ENTAILED"},
    {"claim": "Subletting is permitted.", "evidence": "Tenant shall not sublet the property.", "expected": "CONTRADICTED"},
    {"claim": "Deposit is refundable.", "evidence": "Security deposit will be returned minus damages.", "expected": "ENTAILED"},
    {"claim": "Utilities included.", "evidence": "Tenant is responsible for water and electricity.", "expected": "CONTRADICTED"},
    {"claim": "Jurisdiction is Texas.", "evidence": "Governed by the laws of the State of Texas.", "expected": "ENTAILED"},
    {"claim": "Signatures required.", "evidence": "Agreement must be signed by both parties.", "expected": "ENTAILED"},
    {"claim": "NDA applies for 2 years.", "evidence": "Confidentiality holds for two years post-term.", "expected": "ENTAILED"},
    {"claim": "Arbitration is mandatory.", "evidence": "Any disputes will be resolved in court.", "expected": "CONTRADICTED"},
    {"claim": "Notice via email is valid.", "evidence": "Notice must be sent via certified mail.", "expected": "CONTRADICTED"},
    {"claim": "Renewal is automatic.", "evidence": "Lease renews automatically unless cancelled.", "expected": "ENTAILED"},
    {"claim": "Insurance is optional.", "evidence": "Tenant must maintain renter's insurance.", "expected": "CONTRADICTED"},
    {"claim": "Keys must be returned.", "evidence": "Tenant agrees to surrender keys upon exit.", "expected": "ENTAILED"},
    {"claim": "Modifications allowed with consent.", "evidence": "Alterations require prior written approval.", "expected": "ENTAILED"},
    {"claim": "Guest limit is 3 days.", "evidence": "Guests may stay no longer than 72 hours.", "expected": "ENTAILED"},
    {"claim": "Quiet hours start at 10 PM.", "evidence": "Noise restricted between 22:00 and 08:00.", "expected": "ENTAILED"},
    {"claim": "Parking is free.", "evidence": "Parking space available for $50/month.", "expected": "CONTRADICTED"},

    # --- MEDICAL REPORTS (20) ---
    {"claim": "Patient has hypertension.", "evidence": "Diagnosis: High blood pressure.", "expected": "ENTAILED"},
    {"claim": "Prescribed 500mg Amoxicillin.", "evidence": "Rx: Amoxicillin 500mg TID.", "expected": "ENTAILED"},
    {"claim": "No allergies reported.", "evidence": "Patient is allergic to Penicillin.", "expected": "CONTRADICTED"},
    {"claim": "Follow up in 1 month.", "evidence": "Return to clinic in 4 weeks.", "expected": "ENTAILED"},
    {"claim": "Symptoms include fever.", "evidence": "Patient denies fever or chills.", "expected": "CONTRADICTED"},
    {"claim": "Surgery scheduled for Monday.", "evidence": "Operation planned for next Tuesday.", "expected": "CONTRADICTED"},
    {"claim": "Condition matches flu.", "evidence": "Symptoms consist with influenza.", "expected": "ENTAILED"},
    {"claim": "Blood type is O+.", "evidence": "Blood Group: O Positive.", "expected": "ENTAILED"},
    {"claim": "Keep leg elevated.", "evidence": "Maintain limb elevation to reduce swelling.", "expected": "ENTAILED"},
    {"claim": "Take with meals.", "evidence": "Consume on an empty stomach.", "expected": "CONTRADICTED"},
    {"claim": "Vaccination is complete.", "evidence": "Patient requires booster shot.", "expected": "CONTRADICTED"},
    {"claim": "Weight is 70kg.", "evidence": "Patient weighs 70 kilograms.", "expected": "ENTAILED"},
    {"claim": "MRI results normal.", "evidence": "MRI scan showed no abnormalities.", "expected": "ENTAILED"},
    {"claim": "Fracture in left arm.", "evidence": "X-ray confirms break in left radius.", "expected": "ENTAILED"},
    {"claim": "History of diabetes.", "evidence": "No family history of diabetes.", "expected": "CONTRADICTED"}, # Context trap
    {"claim": "Avoid alcohol.", "evidence": "Do not consume alcoholic beverages.", "expected": "ENTAILED"},
    {"claim": "Pain level is 8/10.", "evidence": "Patient reports severe pain (8 out of 10).", "expected": "ENTAILED"},
    {"claim": "Start physical therapy.", "evidence": "Referral to PT provided.", "expected": "ENTAILED"},
    {"claim": "Diet should be low sodium.", "evidence": "Recommended a low-salt diet.", "expected": "ENTAILED"},
    {"claim": "Discharge today.", "evidence": "Patient will be discharged tomorrow.", "expected": "CONTRADICTED"},

    # --- NEWS & EVENTS (20) ---
    {"claim": "The merger was canceled.", "evidence": "The companies called off the merger.", "expected": "ENTAILED"},
    {"claim": "Stocks rose by 2%.", "evidence": "Market saw a 2% gain.", "expected": "ENTAILED"},
    {"claim": "Storm hit Florida.", "evidence": "Hurricane made landfall in Miami.", "expected": "ENTAILED"},
    {"claim": "Election held on Tuesday.", "evidence": "Voters went to polls on Tuesday.", "expected": "ENTAILED"},
    {"claim": "New bridge opened.", "evidence": "The old bridge was consolidated.", "expected": "NEUTRAL"}, # Tricky
    {"claim": "Protest was peaceful.", "evidence": "Demonstration turned violent.", "expected": "CONTRADICTED"},
    {"claim": "Senator voted Yes.", "evidence": "Senator voted in favor.", "expected": "ENTAILED"},
    {"claim": "Company filed for bankruptcy.", "evidence": "Firm declared Chapter 11.", "expected": "ENTAILED"},
    {"claim": "Winner is France.", "evidence": "France took home the trophy.", "expected": "ENTAILED"},
    {"claim": "Fire contained.", "evidence": "Blaze is 100% contained.", "expected": "ENTAILED"},
    {"claim": "CEO resigned.", "evidence": "Chief Executive stepped down.", "expected": "ENTAILED"},
    {"claim": "Product launched in Asia.", "evidence": "Product debuted in Europe.", "expected": "CONTRADICTED"},
    {"claim": "Treaty signed in Paris.", "evidence": "Agreement inked in the French capital.", "expected": "ENTAILED"},
    {"claim": "No injuries reported.", "evidence": "Several people were hurt.", "expected": "CONTRADICTED"},
    {"claim": "Festival starts at noon.", "evidence": "Event begins at 12:00 PM.", "expected": "ENTAILED"},
    {"claim": "Traffic is heavy.", "evidence": "Roads are clear.", "expected": "CONTRADICTED"},
    {"claim": "Airport closed.", "evidence": "Flights are grounded.", "expected": "ENTAILED"},
    {"claim": "Suspect arrested.", "evidence": "Police detained the suspect.", "expected": "ENTAILED"},
    {"claim": "Movie won 3 awards.", "evidence": "Film received three Oscars.", "expected": "ENTAILED"},
    {"claim": "Local school closed.", "evidence": "Classes cancelled at local high school.", "expected": "ENTAILED"},

    # --- TECHNICAL SPECS (20) ---
    {"claim": "Supports USB 3.0.", "evidence": "Compatible with USB 3.0 devices.", "expected": "ENTAILED"},
    {"claim": "Requires iOS 15.", "evidence": "Minimum requirement: iOS 14 or later.", "expected": "CONTRADICTED"}, # 14 is min, so 15 works but isn't REQUIRED strictly? No, Claim says "Requires 15", evidence says "14+". If I have 14, claim says I can't use it, evidence says I can. Contradiction.
    {"claim": "Battery is removable.", "evidence": "Battery is non-user replaceable.", "expected": "CONTRADICTED"},
    {"claim": "Screen size 6 inches.", "evidence": "Display measures 6.1 inches.", "expected": "CONTRADICTED"}, # Precision check
    {"claim": "Comes in Black.", "evidence": "Available in Midnight color.", "expected": "ENTAILED"}, # Semantic
    {"claim": "Water resistant.", "evidence": "Rated IP67.", "expected": "ENTAILED"},
    {"claim": "No headphone jack.", "evidence": "3.5mm jack is absent.", "expected": "ENTAILED"},
    {"claim": "Update is free.", "evidence": "Free software update available.", "expected": "ENTAILED"},
    {"claim": "Connects via Bluetooth.", "evidence": "Supports Bluetooth 5.0 pairing.", "expected": "ENTAILED"},
    {"claim": "Storage expandable.", "evidence": "No SD card slot.", "expected": "CONTRADICTED"},
    {"claim": "Resolution 1080p.", "evidence": "Full HD 1920x1080.", "expected": "ENTAILED"},
    {"claim": "Warranty 1 year.", "evidence": "12-month manufacturer warranty.", "expected": "ENTAILED"},
    {"claim": "Made of aluminum.", "evidence": "Constructed from alloy.", "expected": "NEUTRAL"}, # Alloy could be anything
    {"claim": "Supports 5G.", "evidence": "4G LTE only.", "expected": "CONTRADICTED"},
    {"claim": "Charger included.", "evidence": "Power adapter in box.", "expected": "ENTAILED"},
    {"claim": "Dual SIM.", "evidence": "Single Nano-SIM slot.", "expected": "CONTRADICTED"},
    {"claim": "Faces ID supported.", "evidence": "Features facial recognition.", "expected": "ENTAILED"},
    {"claim": "Weight 200g.", "evidence": "Weighs 190 grams.", "expected": "CONTRADICTED"},
    {"claim": "Release year 2023.", "evidence": "Launched in 2023.", "expected": "ENTAILED"},
    {"claim": "Works with Alexa.", "evidence": "Google Assistant compatible only.", "expected": "CONTRADICTED"}
]

BENCHMARK_200 = PREV_100 + NEW_100
