import os
import requests
import json
from bs4 import BeautifulSoup
import re

# --- CONFIG ---
API_URL = "https://laws-gateway.moj.gov.sa/apis/legislations/v1/statute/get-Statute-gateway-Detail"
LAWS_JSON_FILE = os.path.join(os.path.dirname(__file__), "laws.json")
BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# Arabic type mapping to folder names
TYPE_TO_FOLDER = {
    "نظام": "laws",
    "لائحة": "regulations",
    "قواعد": "rules",
    "تنظيم": "bylaws",
    "آلية": "mechanisms"
}

# --- HELPER FUNCTION TO EXTRACT STRUCTURED DATA ---
def extract_structured_data(item, parent_path=None):
    if parent_path is None:
        parent_path = []
    
    records = []
    
    # Get the title/sequence for the current node (e.g., "الفصل الأول" or "المادة 1")
    node_name = item.get("name") or ""
    if "sequence" in item and item["sequence"]:
        node_name = f"{item['sequence']} {node_name}".strip()
        
    current_path = parent_path + [node_name] if node_name else parent_path
    
    # Extract and clean text if present
    text = ""
    if "text" in item and item["text"]:
        raw_text = BeautifulSoup(item["text"], "html.parser").get_text(separator="\n").strip()
        text = clean_statute_text(raw_text)
    
    # If the node has text, save it as a structured record
    if text:
        records.append({
            "hierarchy": current_path,
            "title": node_name,
            "text": text
        })
        
    # Recurse into children
    for sub in item.get("items") or []:
        if sub:
            records.extend(extract_structured_data(sub, current_path))
            
    return records

# --- CLEAN FORMATTING FUNCTION ---
def clean_statute_text(text):
    # Collapse multiple blank lines
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    # Strip spaces at start/end of lines
    text = "\n".join(line.strip() for line in text.splitlines())
    # Normalize Arabic numbering bullets (١. → ١))
    text = re.sub(r'([١٢٣٤٥٦٧٨٩٠])\.', r'\1)', text)
    # Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove spaces before punctuation
    text = re.sub(r'\s+([:،؛؟])', r'\1', text)
    return text

# --- MAIN SCRIPT ---
def main(force_update=False, target_serial=None):
    # Load the list of laws
    if not os.path.exists(LAWS_JSON_FILE):
        print(f"Error: {LAWS_JSON_FILE} not found!")
        return

    with open(LAWS_JSON_FILE, "r", encoding="utf-8") as f:
        laws_list = json.load(f)

    headers = {"User-Agent": "Mozilla/5.0"}

    for item in laws_list:
        serial = item.get("serial")
        title = item.get("title", "Unknown_Law").strip()
        law_type = item.get("type", "other").strip()

        if not serial:
            continue
            
        # If a specific target is set, skip the rest
        if target_serial and serial != target_serial:
            continue

        # Map the type to a folder inside data/
        folder_name = TYPE_TO_FOLDER.get(law_type, "other")
        output_dir = os.path.join(BASE_DATA_DIR, folder_name)
        os.makedirs(output_dir, exist_ok=True)

        # Create a safe filename by removing illegal windows characters
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        output_file = os.path.join(output_dir, f"{safe_title}.json")

        if os.path.exists(output_file) and not force_update:
            print(f"Skipping (already exists): {output_file}")
            continue

        print(f"Fetching: {title} ({law_type})...")
        params = {
            "Serial": serial,
            "identityNumber": ""
        }

        try:
            resp = requests.get(API_URL, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            statute_structure = data.get("model", {}).get("statuteStructure", [])
            if not statute_structure:
                print(f"  -> No content found for {title}.")
                continue

            all_records = []
            law_title = data.get("model", {}).get("name", title)

            for section in statute_structure:
                records = extract_structured_data(section, parent_path=[law_title])
                all_records.extend(records)

            # Save the document structured JSON
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_records, f, ensure_ascii=False, indent=4)

            print(f"  -> Saved {len(all_records)} articles to {folder_name}/{safe_title}.json")

        except Exception as e:
            print(f"  -> Error processing {title}: {e}")

if __name__ == "__main__":
    main()