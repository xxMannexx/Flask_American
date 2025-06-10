from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
import io


def crear_pdf(nombre,numero_tarjeta,id_usuario,fecha,monto,tasa,plazo):

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()



    file_name = f"{id_usuario}_Prestamo.pdf"
    document = SimpleDocTemplate(buffer, pagesize=letter)

    margen4_izq = 72  # 2.54 cm
    margen_der = 72
    margen_sup = 72
    margen_inf = 72


    espaciado_parrafo = 12
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 12
    normal_style.leading = espaciado_parrafo

    heading_style = ParagraphStyle(
        'Heading1',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=1,  # Centrado
        spaceAfter=espaciado_parrafo * 2
    )


    subheading_style = ParagraphStyle(
        'Heading2',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=0,  # Alineación a la izquierda
        spaceAfter=espaciado_parrafo
    )


    contenido = []


    contenido.append(Paragraph(
        "American Express Company (México), S.A. de C.V.", heading_style))
    contenido.append(Paragraph(
        "Av. Ejército Nacional 843-B, Col. Granada, Miguel Hidalgo, C.P. 11520, Ciudad de México", normal_style))

    # Fecha
    contenido.append(Paragraph(f"<b>{fecha}</b>", normal_style))

    # Asunto
    contenido.append(Paragraph(
        "<b>Asunto:</b> Confirmación de Aprobación de Solicitud de Préstamo Personal", subheading_style))


    texto_cuerpo = f"""
        Estimado(a) <b>{nombre}</b>,<br/><br/>
        Por medio de la presente, nos complace informarle que su solicitud de préstamo personal ha sido aprobada de manera satisfactoria por American Express tras un análisis exhaustivo de su perfil crediticio, historial financiero y capacidad de pago. Nos honra contar con su confianza y reiteramos nuestro compromiso con ofrecerle soluciones financieras a la medida de sus necesidades.<br/><br/>
        A continuación, se detallan las condiciones específicas del préstamo autorizado:<br/><br/>
        <b>- Número de Tarjeta:</b> {numero_tarjeta}<br/>
        <b>- Fecha de aprobación:</b> {fecha}<br/>
        <b>- Monto total aprobado:</b> {monto}<br/>
        <b>- Tasa de interés anual fija:</b> {tasa}%<br/>
        <b>- Plazo de pago:</b> {plazo} meses<br/><br/>
        El monto será depositado directamente en su cuenta dentro de un plazo no mayor a 24 horas hábiles a partir de la fecha de esta notificación. Es importante que conserve esta carta como constancia oficial de la operación aprobada.<br/><br/>
        En caso de tener cualquier duda sobre su préstamo, fechas de pago, opciones de liquidación anticipada o cualquier otro tema relacionado, ponemos a su disposición nuestros canales de atención personalizada a través del número 01-800-AMEX-MX o en nuestro sitio web oficial.<br/><br/>
        Agradecemos sinceramente su preferencia y reiteramos nuestro compromiso de acompañarle en cada paso de su crecimiento financiero.<br/><br/>
        Atentamente,<br/><br/>
        Departamento de Crédito y Finanzas<br/>
        American Express México
    """

    contenido.append(Paragraph(texto_cuerpo, normal_style))


    contenido.append(Paragraph("<br/><br/>", normal_style))
    contenido.append(Paragraph("<br/><br/>", normal_style))
    contenido.append(Paragraph("<br/>_____________________________________ <br/>", heading_style))
    contenido.append(Paragraph(f"Firma de {nombre}<br/>",heading_style ))

    document.build(contenido)
    buffer.seek(0)

    return buffer









