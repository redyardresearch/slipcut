import datetime
import re
import zipfile
from flask import Flask, request, send_file, render_template
from pypdf import PdfReader, PdfWriter

app = Flask(__name__)

"""
Payslip splitter and decoder, v1.0
Licensed under the GNU Affero General Public License v3.0
Copyright (C) 2025 Red Yard Research S.r.l.
"""

import io

def process_pdf(pdf_file_stream):
    zip_buffer = io.BytesIO()
    skipped_pages = []
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        try:
            pdf = PdfReader(pdf_file_stream)
            file_base_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            for page_num in range(min(pdf.get_num_pages(), 250)):
                pdf_writer = PdfWriter()
                page_obj = pdf.get_page(page_num)
                pdf_writer.add_page(page_obj)

                pdf_text = page_obj.extract_text()
                try:
                    cf_match = re.findall(
                        "(?:[A-Z][AEIOU][AEIOUX]|[AEIOU]X{2}|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}(?:[0-9LMNP-V]{2}(?:[A-EHLMPR-T](?:"
                        "[04LQ][1-9MNP-V]|[15MR][0-9LMNP-V]|[26NS][0-8LMNP-U])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM]|"
                        "[AC-EHLMPR-T][26NS][9V])|(?:[02468LNQSU][048LQU]|[13579MPRTV][26NS])B[26NS][9V])(?:[A-MZ][1-9MNP-V]"
                        "[0-9LMNP-V]{2}|[A-M][0L](?:[1-9MNP-V][0-9LMNP-V]|[0L][1-9MNP-V]))[A-Z]",
                        pdf_text, re.I)
                    if not cf_match:
                        skipped_pages.append(page_num)
                        continue  # skip page if CF not found
                    cf = cf_match[0].replace('\n', '')

                    mese_anno_match = re.findall(
                        "((gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\\s+"
                        "([0-9]{4}))",
                        pdf_text, re.I)
                    if not mese_anno_match:
                        skipped_pages.append(page_num)
                        continue  # skip page if month/year not found
                    (mese_anno, mese_orig, anno) = mese_anno_match[0]
                    mese_dict = {
                        "GENNAIO": "01", "FEBBRAIO": "02", "MARZO": "03", "APRILE": "04", "MAGGIO": "05", "GIUGNO": "06",
                        "LUGLIO": "07", "AGOSTO": "08", "SETTEMBRE": "09", "OTTOBRE": "10", "NOVEMBRE": "11", "DICEMBRE": "12"
                    }.get(mese_orig.upper(), "ZZ")
                except:
                    skipped_pages.append(page_num)
                    continue  # skip page on any unexpected error

                folder_path = f'{cf.upper()}/{anno}{mese_dict}'
                output_file_name = f'{file_base_name}_page_{page_num + 1}.pdf'
                pdf_bytes = io.BytesIO()
                pdf_writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                zipf.writestr(f'{folder_path}/{output_file_name}', pdf_bytes.read())

            # if there are more than 250 pages, add a note as a text file in the zip
            if pdf.get_num_pages() > 250:
                note_text = f'The original PDF has {pdf.get_num_pages()} pages, but only the first 250 pages were processed.'
                zipf.writestr('note.txt', note_text)
            # if there are skipped pages, add a note as a text file in the zip
            if skipped_pages:
                skipped_text = f'The following pages were skipped due to missing data: {", ".join(map(str, skipped_pages))}'
                zipf.writestr('skipped_pages.txt', skipped_text)
        except:
        # return en empty zip with a note if there was an error processing the PDF
            zipf.writestr('error.txt', 'An error occurred while processing the PDF file. Please check the file format and content.')
    # Reset the buffer position to the beginning
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    #check if the file is a PDF and less than 10MB
    if not file.filename.lower().endswith('.pdf'):
        return "File is not a PDF", 400
    if file.content_length > 10 * 1024 * 1024:
        return "File is too large, must be less than 10MB", 400

    # make a filestream from the file
    file_stream = io.BytesIO()
    file.save(file_stream)
    file_stream.seek(0)

    zip_file = process_pdf(file_stream)
    return send_file(zip_file, as_attachment=True, mimetype='application/zip', download_name='processed_files.zip')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)