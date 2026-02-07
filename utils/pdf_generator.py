from io import BytesIO
from xhtml2pdf import pisa
from flask import render_template, make_response

def render_pdf(template_name, context, filename="report.pdf"):
    """
    Render a PDF from an HTML template.
    
    Args:
        template_name (str): Path to the HTML template (e.g., 'reports/pdf_timetable.html')
        context (dict): Dictionary of variables to pass to the template
        filename (str): Filename for the downloaded PDF
        
    Returns:
        Response: Flask response object with PDF content
    """
    html = render_template(template_name, **context)
    result = BytesIO()
    
    # Generate PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    
    return None
