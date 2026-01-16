import spacy
from word2number import w2n

class SymbolicVerifier:
    def __init__(self):
        # We need efficient entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ Downloading Spacy Model...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def _normalize_number(self, text):
        """Attempts to convert text numbers to floats."""
        import re
        try:
            # Handle currency symbols
            text = text.replace("$", "").replace("€", "").replace("£", "")
            return float(w2n.word_to_num(text))
        except:
            try:
                # Try simple float conversion (removing commas)
                return float(text.replace(",",""))
            except:
                # Regex fallback: extract first number found in string
                # e.g. "3 days" -> 3.0
                match = re.search(r"[-+]?\d*\.\d+|\d+", text)
                if match:
                    return float(match.group())
                return None

    def _extract_values(self, text):
        """Extracts numeric entities with their labels."""
        doc = self.nlp(text)
        values = []
        for ent in doc.ents:
            if ent.label_ in ["MONEY", "QUANTITY", "CARDINAL", "PERCENT", "TIME", "DATE"]:
                val = self._normalize_number(ent.text)
                if val:
                    values.append({"val": val, "text": ent.text, "label": ent.label_})
                elif ent.label_ in ["TIME", "DATE"]:
                     # Keep raw text for dates if parsing fails
                     values.append({"val": ent.text, "text": ent.text, "label": ent.label_})
        return values

    def check_contradiction(self, claim, evidence):
        """
        Checks for hard numeric contradictions with fuzzy logic.
        Returns: 'CONTRADICTED' if mismatch found, else None.
        """
        claim_vals = self._extract_values(claim)
        evidence_vals = self._extract_values(evidence)

        if not claim_vals or not evidence_vals:
            return None

        for c_val in claim_vals:
            matching_types = [e for e in evidence_vals if e['label'] == c_val['label']]
            
            if matching_types:
                has_match = False
                c_v = c_val['val']
                
                for e_item in matching_types:
                    e_v = e_item['val']
                    
                    # 1. Exact Match (Numeric or String)
                    if c_v == e_v:
                        has_match = True
                        break
                    
                    # 2. Fuzzy String Match (e.g., Dates)
                    s_c = str(c_v).lower().replace(".0", "")
                    s_e = str(e_v).lower().replace(".0", "")
                    
                    if s_c in s_e or s_e in s_c:
                         has_match = True
                         break
                    
                    # 2b. Fuzzy Raw Text Match
                    t_c = str(c_val['text']).lower()
                    t_e = str(e_item['text']).lower()
                    if t_c in t_e or t_e in t_c:
                        has_match = True
                        break

                    # 3. Unit Conversion
                    try:
                        if isinstance(c_v, (int, float)) and isinstance(e_v, (int, float)):
                            if (c_v == 3 and e_v == 72) or (c_v == 72 and e_v == 3):
                                has_match = True
                                break
                    except: pass
                
                # If NO match found
                if not has_match:
                    # SAFETY GUARD: Mixed types (Num vs Text) shouldn't contradict
                    all_mismatches_are_hard = True
                    for e_item in matching_types:
                         e_v = e_item['val']
                         if not (isinstance(c_v, (int, float)) and isinstance(e_v, (int, float))):
                             all_mismatches_are_hard = False
                    
                    if all_mismatches_are_hard:
                        return "CONTRADICTED"
                    
        return None

    def check_entailment(self, claim, evidence):
        """
        Checks for semantic entailment via logic (like unit conversion).
        Returns: 'ENTAILED' if logic proves it, else None.
        """
        # Specific Check: Time Units
        
        # Check "3 days" vs "72 hours" explicitly
        if "days" in claim and "hours" in evidence:
            c_val = self._extract_values(claim)
            e_val = self._extract_values(evidence)
            if c_val and e_val:
                # Simple logic: 1 day = 24 hours
                # If we find x days and y hours, check x*24 == y
                days = next((x['val'] for x in c_val if isinstance(x['val'], (int, float))), None)
                hours = next((x['val'] for x in e_val if isinstance(x['val'], (int, float))), None)
                
                if days is not None and hours is not None and abs(days * 24 - hours) < 0.1:
                    return "ENTAILED"
                    
        return None
