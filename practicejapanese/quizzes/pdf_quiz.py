# pdf_quiz.py
# Quiz module using content from a split PDF

import PyPDF2
import os
import importlib.resources


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
    # Use importlib.resources to access bundled PDFs
    pdf_name = os.path.basename(input_pdf_path)
    output_pdf_path = None
    pdf_path = None
    # Try package resources first
    try:
        with importlib.resources.path('practicejapanese.public', pdf_name) as pkg_pdf_path:
            pdf_path = str(pkg_pdf_path)
            output_pdf_path = os.path.join(os.path.dirname(pdf_path), 'split_output.pdf')
    except FileNotFoundError:
        # Fallback: check current working directory
        cwd_pdf_path = os.path.join(os.getcwd(), pdf_name)
        if os.path.exists(cwd_pdf_path):
            pdf_path = cwd_pdf_path
            output_pdf_path = os.path.join(os.getcwd(), 'split_output.pdf')
        else:
            # Fallback: check $HOME/public/
            home_pdf_path = os.path.join(os.path.expanduser('~'), 'public', pdf_name)
            if os.path.exists(home_pdf_path):
                pdf_path = home_pdf_path
                output_pdf_path = os.path.join(os.path.dirname(home_pdf_path), 'split_output.pdf')
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"PDF file '{pdf_name}' not found in package resources, current directory, or $HOME/public/. Please provide a valid PDF.")
        return []
    split_pdf(pdf_path, output_pdf_path, start_page, end_page)
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
    input_pdf_path = '2Shin_Kanzen_Masuta_N2-Goi.pdf'
    start_page = 10
    end_page = 13
    quiz_from_pdf(input_pdf_path, start_page, end_page)
