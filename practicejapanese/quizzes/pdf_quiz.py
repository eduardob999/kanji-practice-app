# pdf_quiz.py
# Quiz module using content from a split PDF

import PyPDF2
import os
import importlib.resources


def _public_assets_dir():
    """
    Preferred location for public assets after installation.
    We copy bundled assets there during install (~/Public/PracticeJapanese).
    """
    home = os.path.expanduser('~')
    # Prefer 'Public' (common on Linux/macOS). Fall back to lowercase if needed at runtime.
    pub = os.path.join(home, 'Public')
    if not os.path.exists(pub):
        alt = os.path.join(home, 'public')
        pub = alt if os.path.exists(alt) else pub
    target = os.path.join(pub, 'PracticeJapanese')
    # Ensure dir exists for outputs
    try:
        os.makedirs(target, exist_ok=True)
    except Exception:
        pass
    return target


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
    # Prefer assets from user's Public folder installed at setup time
    pdf_name = os.path.basename(input_pdf_path)
    public_dir = _public_assets_dir()
    pdf_path = os.path.join(public_dir, pdf_name)
    output_pdf_path = os.path.join(public_dir, 'split_output.pdf')

    if not os.path.exists(pdf_path):
        # Fallback to packaged resources
        try:
            with importlib.resources.path('practicejapanese.public', pdf_name) as pkg_pdf_path:
                # Copy to public dir for future runs
                try:
                    import shutil
                    shutil.copy2(str(pkg_pdf_path), pdf_path)
                except Exception:
                    pass
                pdf_path = str(pkg_pdf_path)
        except FileNotFoundError:
            # Fallback: current working directory
            cwd_pdf_path = os.path.join(os.getcwd(), pdf_name)
            if os.path.exists(cwd_pdf_path):
                pdf_path = cwd_pdf_path
            else:
                # Fallback: $HOME/Public and $HOME/public
                for candidate in [
                    os.path.join(os.path.expanduser('~'), 'Public', pdf_name),
                    os.path.join(os.path.expanduser('~'), 'public', pdf_name),
                ]:
                    if os.path.exists(candidate):
                        pdf_path = candidate
                        break

    if not pdf_path or not os.path.exists(pdf_path):
        print(f"PDF file '{pdf_name}' not found in ~/Public/PracticeJapanese, package resources, cwd, or home Public. Provide a valid PDF.")
        return []
    split_pdf(pdf_path, output_pdf_path, start_page, end_page)
    # Check if the split PDF file was written successfully
    print(f"[DEBUG] After split_pdf: output_pdf_path = {output_pdf_path}")
    print(f"[DEBUG] Split PDF exists: {os.path.exists(output_pdf_path)}")
    # Open the split PDF file
    def open_pdf(filepath):
        print(f"[DEBUG] Attempting to open PDF: {filepath}")
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print(f"[DEBUG] os.environ: {os.environ}")
        print(f"[DEBUG] File exists: {os.path.exists(filepath)}")
        if 'TERMUX_VERSION' in os.environ:
            print("[DEBUG] Detected Termux environment.")
            try:
                import subprocess
                print(f"[DEBUG] Running: termux-open {filepath}")
                result = subprocess.run(['termux-open', filepath], check=True, capture_output=True, text=True)
                print(f"[DEBUG] termux-open stdout: {result.stdout}")
                print(f"[DEBUG] termux-open stderr: {result.stderr}")
            except Exception as e:
                print(f"Failed to open PDF with termux-open: {e}\nMake sure you have a PDF viewer app installed.")
        else:
            print("[DEBUG] Not a Termux environment. Using xdg-open.")
            try:
                import subprocess
                print(f"[DEBUG] Running: xdg-open {filepath}")
                result = subprocess.run(['xdg-open', filepath], check=True, capture_output=True, text=True)
                print(f"[DEBUG] xdg-open stdout: {result.stdout}")
                print(f"[DEBUG] xdg-open stderr: {result.stderr}")
            except Exception as e:
                print(f"Failed to open PDF with xdg-open: {e}\nYou may need to install a PDF viewer or desktop-file-utils. Try running 'sudo apt install desktop-file-utils' and 'sudo apt install xpdf' or another PDF viewer.")
    open_pdf(output_pdf_path)
    print(f"[DEBUG] PDF split and opened: {output_pdf_path}")
    # No text extraction or question printing

# Example usage
if __name__ == "__main__":
    input_pdf_path = '2Shin_Kanzen_Masuta_N2-Goi.pdf'
    start_page = 10
    end_page = 13
    quiz_from_pdf(input_pdf_path, start_page, end_page)
