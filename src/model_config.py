# src/model_config.py

# Prioritized list of models found in your specific account logs
# We put "Lite" and "001" versions first as they are usually most stable
MODEL_ROSTER = [
    'gemini-2.0-flash-lite-preview-02-05', # Very specific, likely fresh quota
    'gemini-2.0-flash-001',                # Stable 2.0
    'gemini-2.0-flash-lite-001',           # Stable Lite
    'gemini-exp-1206',                     # Experimental (often separate quota)
    'gemini-2.0-flash-lite',               # Generic Lite
    'gemini-2.0-flash',                    # Generic Flash
    'gemini-2.0-flash-exp',                # Flash Exp
]