import os
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFGenerator:
    @staticmethod
    def generate_ce_certificate(cert_uuid: str, product_name: str, model_number: str, company_name: str, directive_code: str, payload_hash: str, tx_hash: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        qr_data = f"https://certice.verifier/verify/{cert_uuid}"
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="navy", back_color="white")
        qr_temp_path = f"/tmp/qr_{cert_uuid}.png"
        qr_img.save(qr_temp_path)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0f172a'),
            alignment=1,
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            alignment=1,
            spaceAfter=25
        )
        
        elements = []
        elements.append(Paragraph("<b>EU DECLARATION OF CONFORMITY (CE)</b>", title_style))
        elements.append(Paragraph("Issued under ISO/IEC 17050-1 & Authenticated via CertiCE Blockchain Ledger", subtitle_style))
        elements.append(Spacer(1, 15))
        
        data = [
            ["Certificate UUID:", cert_uuid],
            ["Manufacturer:", company_name],
            ["Product Name:", product_name],
            ["Model Number:", model_number],
            ["Applied EU Directive:", directive_code],
            ["Harmonized Standard:", "EN ISO 12100:2010 (Risk Assessment)"],
            ["Payload SHA-256 Hash:", payload_hash[:32] + "..."],
            ["Blockchain Tx Hash:", tx_hash[:32] + "..."],
            ["Status:", "VERIFIED & IMMUTABLE"]
        ]
        
        t = Table(data, colWidths=[160, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Image(qr_temp_path, width=90, height=90))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("Scan QR Code to verify certificate authenticity on Blockchain Ledger", subtitle_style))
        
        doc.build(elements)
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)
            
        return output_path
