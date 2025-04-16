import csv
import io
import json
from weasyprint import HTML
from markdown import markdown
from bs4 import BeautifulSoup

def export_to_pdf(markdown_content, title):
    """Convert markdown content to PDF"""
    # Convert markdown to HTML
    html_content = markdown(markdown_content)
    
    # Create a complete HTML document with styles
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 2cm;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #333;
                margin-top: 1.5em;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
                text-align: left;
            }}
            code {{
                background-color: #f5f5f5;
                padding: 0.2em 0.4em;
                border-radius: 3px;
            }}
            pre {{
                background-color: #f5f5f5;
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    pdf_file = io.BytesIO()
    HTML(string=styled_html).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    return pdf_file

def extract_tables_to_csv(markdown_content):
    """Extract tables from markdown content and convert to CSV"""
    # Convert markdown to HTML
    html_content = markdown(markdown_content)
    
    # Parse HTML to find tables
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    
    if not tables:
        return None
    
    # Process each table into CSV
    csv_files = []
    for i, table in enumerate(tables):
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Extract and write headers
        headers = [th.get_text().strip() for th in table.find_all('th')]
        if headers:
            csv_writer.writerow(headers)
        
        # Extract and write rows
        for row in table.find_all('tr'):
            cells = [td.get_text().strip() for td in row.find_all('td')]
            if cells:
                csv_writer.writerow(cells)
        
        # Create BytesIO object for each CSV
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        csv_files.append((f"table_{i+1}.csv", csv_bytes))
    
    return csv_files

def export_to_json(analysis_data):
    """Export analysis data to JSON format"""
    json_data = json.dumps(analysis_data, indent=2)
    json_bytes = io.BytesIO()
    json_bytes.write(json_data.encode('utf-8'))
    json_bytes.seek(0)
    return json_bytes