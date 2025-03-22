import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
import json
import os
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

def extract_text_from_pdf(pdf_path):
    """Extracts text from each page while preserving formatting."""
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # Preserve layout
        cleaned_text = clean_text(text)  # Remove headers & footers
        extracted_text[f"Page {page_num + 1}"] = cleaned_text

    return extracted_text

def extract_tables_from_pdf(pdf_path):
    """Extracts tables from PDF while preserving structure."""
    tables_data = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                tables_data[f"Page {page_num + 1}"] = tables

    return tables_data

def clean_text(text):
    """Removes repetitive headers and footers from text."""
    lines = text.split("\n")
    cleaned_lines = []

    for i, line in enumerate(lines):
        if i < 3 or i > len(lines) - 3:  # Ignore first 3 & last 3 lines (potential header/footer)
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()

def save_to_json(text_data, tables_data, output_path):
    """Saves extracted data into a well-structured JSON file."""
    structured_output = []

    for page_num in text_data.keys():
        page_content = {
            "page_number": page_num.split()[-1],  # Extract number from "Page X"
            "content": text_data[page_num],
            "tables": tables_data.get(page_num, [])
        }
        structured_output.append(page_content)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(structured_output, json_file, indent=4, ensure_ascii=False)

    return output_path

def main():
    st.title("📄 Enhanced PDF Extractor")
    st.write("Upload an Annual Report PDF to extract clean data **page-wise**, removing headers/footers.")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        pdf_path = os.path.join("temp.pdf")
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        # Extract text & tables
        text_data = extract_text_from_pdf(pdf_path)
        tables_data = extract_tables_from_pdf(pdf_path)

        # Save structured JSON
        output_json_path = "clean_extracted_data.json"
        save_to_json(text_data, tables_data, output_json_path)

        # Display extraction results
        st.success("✅ Extraction Completed!")
        st.write("### Extracted Content (Preview):")

        for page in text_data.keys():
            st.subheader(f"📄 Page {page.split()[-1]}")
            st.text_area(f"Text - {page}", text_data[page], height=200)

            if page in tables_data and tables_data[page]:
                st.write(f"📊 **Tables on {page}:**")
                for table in tables_data[page]:
                    st.table(table)

        # Provide Download Link
        with open(output_json_path, "rb") as f:
            st.download_button(
                label="📥 Download Extracted JSON",
                data=f,
                file_name="clean_extracted_data.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
