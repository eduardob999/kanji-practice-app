# pdf_quiz.py
# Quiz module using content from a split PDF

import PyPDF2
import os


def split_pdf(input_pdf_path, output_pdf_path, start_page, end_page):
    with open(input_pdf_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()
        for i in range(start_page - 1, end_page):
            writer.add_page(reader.pages[i])
        with open(output_pdf_path, 'wb') as outfile:
            writer.write(outfile)


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def quiz_from_pdf(input_pdf_path, start_page, end_page):
    package_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(os.path.dirname(package_dir), 'public')
    input_pdf_path = os.path.join(public_dir, os.path.basename(input_pdf_path))
    output_pdf_path = os.path.join(public_dir, 'split_output.pdf')
    split_pdf(input_pdf_path, output_pdf_path, start_page, end_page)
    # Open the split PDF file
    def open_pdf(filepath):
        if 'TERMUX_VERSION' in os.environ:
            try:
                import subprocess
                subprocess.run(['termux-open', filepath], check=True)
            except Exception as e:
                print(f"Failed to open PDF with termux-open: {e}\nMake sure you have a PDF viewer app installed.")
        else:
            try:
                import subprocess
                subprocess.run(['xdg-open', filepath], check=True)
            except Exception as e:
                print(f"Failed to open PDF with xdg-open: {e}\nYou may need to install a PDF viewer or desktop-file-utils. Try running 'sudo apt install desktop-file-utils' and 'sudo apt install xpdf' or another PDF viewer.")
    open_pdf(output_pdf_path)
    text = extract_text_from_pdf(output_pdf_path)
    questions = [line.strip() for line in text.splitlines() if line.strip()]
    print(f"PDF Quiz: {len(questions)} questions extracted from pages {start_page}-{end_page}")
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")
    return questions

# Example usage
if __name__ == "__main__":
    package_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(os.path.dirname(package_dir), 'public')
    input_pdf_path = os.path.join(public_dir, '2Shin_Kanzen_Masuta_N2-Goi.pdf')
    start_page = 10
    end_page = 13
    quiz_from_pdf(input_pdf_path, start_page, end_page)
