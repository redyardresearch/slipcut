# SlipCut: a Payslip Splitter and Decoder

A web application to split and decode Italian payslip PDFs, extracting each page, organizing them by Codice Fiscale and month, and packaging the results in a ZIP file.

## Features

- Upload a multi-page PDF of payslips.
- Automatically detects Codice Fiscale and month/year from each page.
- Splits and organizes pages into folders by employee and period.
- Skips pages with missing data and logs them.
- Supports up to 250 pages per upload.
- No profiling or third-party cookies.

## Usage

1. Run the app locally:
    ```bash
    pip install -r requirements.txt
    python app.py
    ```
   Or with Docker:
    ```bash
    docker build -t payslip-splitter .
    docker run -p 5000:5000 payslip-splitter
    ```

2. Open your browser at [http://localhost:5000](http://localhost:5000).

3. Upload your PDF and download the processed ZIP.

## Requirements

- Python 3.10+
- Flask
- pypdf

See `requirements.txt` for details.

## License

GNU Affero General Public License v3.0  
Copyright (C) 2025 Red Yard Research S.r.l.

## Privacy

This app only uses technical cookies necessary for session management and security (e.g., CSRF token). No profiling or third-party cookies are used.

For questions, visit [https://redyard.com/contatti/](https://redyard.com/contatti/).