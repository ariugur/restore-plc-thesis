import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from docx import Document
from openai import OpenAI

# Load .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SETTINGS
BATCH_SIZE = 20
SLEEP_SECONDS = 3
RETRY_LIMIT = 4
INPUT_FILE = "thesis_tr.docx"
OUTPUT_FILE = "translated_thesis.md"
PROGRESS_FILE = "progress.json"

# Load document
doc = Document(INPUT DOCUMENT")
paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]

# Split into batches
batches = [paragraphs[i:i+BATCH_SIZE] for i in range(0, len(paragraphs), BATCH_SIZE)]

# Load progress if exists
if Path(PROGRESS_FILE).exists():
    with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
        progress = json.load(pf)
    start_index = progress.get("last_completed", -1) + 1
else:
    start_index = 0

print(f"Starting from batch {start_index+1}/{len(batches)}...")

# Main translation loop
with open(OUTPUT_FILE, "a", encoding="utf-8") as out_file:
    for idx, batch in enumerate(batches[start_index:], start=start_index):
        success = False
        attempts = 0
        while not success and attempts < RETRY_LIMIT:
            try:
                input_text = "\n\n".join(batch)
                prompt = f"""
You are a professional academic translator and editor. 
Translate the following Turkish academic text into fluent, formal (target language) 
suitable for a graduate thesis. 
- Ensure the translation reads as if it was originally written in (target language), 
  with clear academic style and natural flow.
- Do NOT add, remove, or change any meaning, data, or argument structure.
- Strictly preserve the original context, logic, and evidential content.
- Maintain all headings, lists, tables and references in their positions.

Now translate the text below:

\"\"\"
{input_text}
\"\"\"
"""
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                translation = response.choices[0].message.content.strip()
                out_file.write(translation + "\n\n")
                
                with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                    json.dump({"last_completed": idx}, pf)
                
                print(f"✅ Batch {idx+1}/{len(batches)} completed.")
                success = True
                time.sleep(SLEEP_SECONDS)
            except Exception as e:
                attempts += 1
                print(f"⚠️ Error on batch {idx+1}: {e}. Retry {attempts}/{RETRY_LIMIT}...")
                time.sleep(SLEEP_SECONDS * attempts)
        
        if not success:
            print(f"❌ Failed to process batch {idx+1} after {RETRY_LIMIT} attempts. Stopping.")
            break

print("🎉 Translation process complete.")
