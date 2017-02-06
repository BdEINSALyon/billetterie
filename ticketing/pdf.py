from datetime import datetime

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from django.http import HttpResponse

from ticketing import security
from ticketing.models import Ticket


def generate_ticket(request, code, **params):

    data = security.decrypt(code)
    ticket = Ticket.objects.get(id=data['ticket']['id'])
    data['time'] = str(datetime.now())
    qr_code = qr.QrCodeWidget(ticket.code())

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket-{}.pdf"'.format(ticket.full_id())

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)

    bounds = qr_code.getBounds()
    qr_width = bounds[2] - bounds[0]
    qr_height = bounds[3] - bounds[1]
    c = Drawing(45, 45, transform=[230. / qr_width, 0, 0, 230. / qr_height, 0, 0])
    c.add(qr_code)
    p.drawImage(ImageReader(ticket.entry.event.ticket_background),
                0, 0,
                width=A4[0], height=A4[1],
                mask='auto', preserveAspectRatio=True)

    qr_x = A4[1] * 0.1
    qr_y = A4[0] * 0.3
    renderPDF.draw(c, p, qr_x, qr_y)
    p.drawString(qr_x + 20, qr_y, "Billet #{}".format(ticket.full_id()))

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    text_x = qr_x + 2.3 * qr_width + 30
    text_y = qr_y + 1.5 * qr_height
    p.drawString(text_x, text_y, "{} {}".format(ticket.first_name, ticket.last_name.upper()))
    p.drawString(text_x, text_y - 20, "{}".format(ticket.email))
    p.drawString(text_x, text_y - 40, "{} (TTC)".format(ticket.entry.full_name()))

    p.setFontSize(10)
    p.drawString(qr_x, qr_y - 50, "Billet vendu et édité par le BdE INSA Lyon, 20 avenue Albert Einstein, "
                                       "69621 Villeurbanne CEDEX".format(ticket.full_id()))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
