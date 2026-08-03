from extract import extract_text

with open("lease_agreement.pdf", "rb") as f:
    file_bytes = f.read()

text = extract_text(file_bytes, "lease_agreement.pdf")
print(text[:1000])
print(f"\n\nTotal characters extracted: {len(text)}")