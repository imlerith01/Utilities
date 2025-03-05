import fitz  # PyMuPDF
from xml.etree import ElementTree as ET
import re
import os
from collections import defaultdict

def extract_xmp_metadata(doc):
    """
    Extract and parse XMP metadata from the PDF document.

    Parameters:
        doc (fitz.Document): The PDF document.

    Returns:
        dict: Parsed XMP metadata.
    """
    try:
        # Retrieve the XML metadata stream
        xmp_metadata = doc.metadata.get("xml")
        if not xmp_metadata:
            print("No XMP metadata found in the document.")
            return {}

        # Parse the XMP metadata as XML
        xmp_tree = ET.ElementTree(ET.fromstring(xmp_metadata))
        xmp_dict = {}
        for elem in xmp_tree.iter():
            # Extract tags and text content from XML elements
            tag = re.sub(r'{.*}', '', elem.tag)  # Remove namespaces
            if elem.text and tag:
                xmp_dict[tag] = elem.text.strip()

        return xmp_dict

    except Exception as e:
        print(f"Error parsing XMP metadata: {e}")
        return {}

def check_pdf_a3b(file_path):
    """
    Checks if the given PDF file is in PDF/A-3b format.

    Parameters:
        file_path (str): The path to the PDF file to check.

    Returns:
        str: A string describing the PDF/A compliance status.
    """
    try:
        # Open the PDF file
        doc = fitz.open(file_path)

        # Attempt to extract XMP metadata
        xmp_data = extract_xmp_metadata(doc)
        if xmp_data:
            pdfaid_part = xmp_data.get("part", "")
            pdfaid_conformance = xmp_data.get("conformance", "")

            if pdfaid_part == "3" and pdfaid_conformance == "B":
                return "PDF/A-3b compliant (based on XMP metadata)"

        # Fallback to catalog checks
        catalog_xref = doc.pdf_catalog()
        output_intents = doc.xref_get_key(catalog_xref, "OutputIntents")[1]
        if not output_intents:
            return "Not PDF/A compliant (no OutputIntents)"
        else:
            output_intents_list = output_intents.strip("[]").split()
            if output_intents_list:
                try:
                    first_intent_xref = int(output_intents_list[0])
                    intent_subtype = doc.xref_get_key(first_intent_xref, "S")[1]
                    if intent_subtype == "/GTS_PDFA1":
                        return "PDF/A compliant (based on OutputIntents)"
                    else:
                        return f"Not PDF/A compliant (OutputIntent S subtype: {intent_subtype})"
                except ValueError:
                    return "Invalid OutputIntents array format"

        # Metadata fallback
        metadata = doc.metadata
        if metadata:
            pdfa_level = metadata.get("pdfa_level", "").upper()
            if pdfa_level == "3B":
                return "PDF/A-3b compliant (based on metadata)"
            elif pdfa_level:
                return f"PDF/A-{pdfa_level} compliant (based on metadata)"

        return "Not PDF/A compliant (no markers found)"

    except Exception as e:
        return f"Error analyzing PDF: {e}"
    finally:
        doc.close()

def analyze_folder(folder_path, output_file="analysis_summary.txt"):
    """
    Analyzes all PDF files in the given folder for PDF/A compliance.

    Parameters:
        folder_path (str): The path to the folder containing PDF files.
        output_file (str): The file to save the analysis summary.

    Returns:
        None
    """
    results = defaultdict(list)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                print(f"Analyzing: {file_path}")
                result = check_pdf_a3b(file_path)
                print(f"Result: {result}\n")
                results[result].append(file_path)

    # Print and save a summary of results
    with open(output_file, "w") as f:
        f.write("--- Analysis Summary ---\n")
        print("\n--- Analysis Summary ---")
        total_files = 0

        for status, files in results.items():
            total_files += len(files)
            f.write(f"{status}: {len(files)} file(s)\n")
            print(f"{status}: {len(files)} file(s)")
            for file in files:
                f.write(f"  - {file}\n")
                print(f"  - {file}")

        f.write(f"\nTotal files analyzed: {total_files}\n")
        print(f"\nTotal files analyzed: {total_files}")

if __name__ == "__main__":
    # Specify the path to the folder containing PDF files
    folder_path = r"C:\Users\dvoracek\DC\ACCDocs\Atelier 99 s.r.o-\ZS Malse\Project Files\002_SDILENE\03_PBR"
    analyze_folder(folder_path)
