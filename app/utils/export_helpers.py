from io import BytesIO
from bs4 import BeautifulSoup
import pandas as pd
from weasyprint import HTML
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def export_to_pdf(report_md, title):
    """
    Convert Markdown report to PDF using WeasyPrint.
    """
    # Convert Markdown to HTML (simple, can be improved)
    try:
        import markdown
    except ImportError:
        raise ImportError('Please install the markdown package for PDF export.')
    html_content = markdown.markdown(report_md)
    html_full = f"""
    <html><head><meta charset='utf-8'><title>{title}</title></head><body>{html_content}</body></html>
    """
    pdf_buffer = BytesIO()
    HTML(string=html_full).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def extract_tables_to_csv(report_md):
    """
    Extract tables from Markdown report, convert to CSV using Pandas, and return a list of (filename, BytesIO) tuples.
    """
    # Convert Markdown to HTML
    try:
        import markdown
    except ImportError:
        raise ImportError('Please install the markdown package for CSV export.')
    html_content = markdown.markdown(report_md, extensions=['tables'])
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    csv_files = []
    for idx, table in enumerate(tables):
        df = pd.read_html(str(table))[0]
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        filename = f'table_{idx+1}.csv'
        csv_files.append((filename, buffer))
    return csv_files 