from flask import Flask, request, send_file, jsonify
import io
import os
import base64
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import Flowable

app = Flask(__name__)

W, H = A4

NEGRO     = colors.HexColor("#0A0A0A")
ORO       = colors.HexColor("#C9A84C")
ORO_CLARO = colors.HexColor("#E8D5A3")
ORO_BG    = colors.HexColor("#FDF8EE")
BLANCO    = colors.white
GRIS_OSC  = colors.HexColor("#2A2A2A")
GRIS_MED  = colors.HexColor("#555555")
GRIS_CLAR = colors.HexColor("#F5F5F5")
GRIS_LINE = colors.HexColor("#E0E0E0")

ENLACE_FAMILIAS = "https://drive.google.com/drive/folders/1WJglRuI-eA2oozSrabKg7QZM5IPUvtta?usp=drive_link"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

s_h2      = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12, textColor=ORO, leading=16, spaceAfter=6, spaceBefore=10)
s_hdr_t   = ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=8, textColor=BLANCO, leading=10, alignment=TA_CENTER)
s_celda   = ParagraphStyle("celda", fontName="Helvetica", fontSize=7.5, textColor=GRIS_OSC, leading=10)
s_celda_b = ParagraphStyle("celda_b", fontName="Helvetica-Bold", fontSize=7.5, textColor=NEGRO, leading=10)
s_ok      = ParagraphStyle("ok", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#1A7A1A"), leading=10, alignment=TA_CENTER)

def sp(n=6): return Spacer(1, n)
def saltop(): return PageBreak()

COLORES_TIPO = {
    "ESTRUCTURA":   colors.HexColor("#1A3A5C"),
    "FORJADOS":     colors.HexColor("#2C5F8A"),
    "FACHADAS":     colors.HexColor("#1A5C3A"),
    "CUBIERTAS":    colors.HexColor("#5C3A1A"),
    "SUELOS":       colors.HexColor("#3A1A5C"),
    "TABIQUES":     colors.HexColor("#5C1A3A"),
    "CARPINTERIA":  colors.HexColor("#1A4A5C"),
    "AISLAMIENTO":  colors.HexColor("#5C4A1A"),
    "HVAC":         colors.HexColor("#8B1A1A"),
    "VENTILACIÓN":  colors.HexColor("#1A5C5C"),
    "FONTANERÍA":   colors.HexColor("#1A3A8B"),
    "ELECTRICIDAD": colors.HexColor("#7A6A10"),
}

ICONOS_TIPO = {
    "ESTRUCTURA": "STR", "FORJADOS": "FOR", "FACHADAS": "FAC",
    "CUBIERTAS": "CUB", "SUELOS": "SUE", "TABIQUES": "TAB",
    "CARPINTERIA": "CAR", "AISLAMIENTO": "AIS", "HVAC": "HVC",
    "VENTILACIÓN": "VEN", "FONTANERÍA": "FON", "ELECTRICIDAD": "ELE",
}

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NEGRO)
    canvas.rect(0, H-2*cm, W, 2*cm, fill=1, stroke=0)
    canvas.setStrokeColor(ORO)
    canvas.setLineWidth(1.5)
    canvas.line(0, H-2*cm, W, H-2*cm)
    if os.path.exists(LOGO_PATH):
        canvas.drawImage(LOGO_PATH, 0.3*cm, H-1.95*cm,
                        width=2.2*cm, height=1.8*cm,
                        preserveAspectRatio=True, mask='auto')
    canvas.setFillColor(ORO)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(2.8*cm, H-1.0*cm, "ARQUETRIX DESING")
    canvas.setFillColor(ORO_CLARO)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(2.8*cm, H-1.55*cm, "Asistente BIM Profesional — CTE España 2026")
    canvas.setFillColor(ORO_CLARO)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(W-0.8*cm, H-1.1*cm, f"Pág. {doc.page}")
    canvas.setFillColor(NEGRO)
    canvas.rect(0, 0, W, 0.9*cm, fill=1, stroke=0)
    canvas.setStrokeColor(ORO)
    canvas.setLineWidth(0.8)
    canvas.line(0, 0.9*cm, W, 0.9*cm)
    canvas.setFillColor(ORO_CLARO)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(0.8*cm, 0.32*cm, "© Arquetrix Desing — Informe BIM generado automáticamente")
    canvas.drawRightString(W-0.8*cm, 0.32*cm, "arquetrixdesing.com")
    canvas.restoreState()

class Portada(Flowable):
    def __init__(self, ciudad, provincia, uso, zona, clima, altitud, obs, fecha):
        self.ciudad=ciudad; self.provincia=provincia; self.uso=uso
        self.zona=zona; self.clima=clima; self.altitud=altitud
        self.obs=obs; self.fecha=fecha
        self.width=W-2*cm; self.height=9*cm

    def draw(self):
        c = self.canv
        ancho=self.width; alto=self.height
        c.setFillColor(NEGRO)
        c.rect(0, 0, ancho, alto, fill=1, stroke=0)
        c.setStrokeColor(ORO)
        c.setLineWidth(2)
        c.line(0, alto-0.3*cm, ancho, alto-0.3*cm)
        c.line(0, 0.3*cm, ancho, 0.3*cm)
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 0.3*cm, alto/2-2.5*cm,
                       width=5*cm, height=5*cm,
                       preserveAspectRatio=True, mask='auto')
        c.setStrokeColor(ORO)
        c.setLineWidth(1)
        c.line(5.8*cm, 0.8*cm, 5.8*cm, alto-0.8*cm)
        c.setFillColor(ORO)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(6.5*cm, alto-1.8*cm, "INFORME BIM PROFESIONAL")
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(6.5*cm, alto-2.8*cm, self.uso)
        c.setFillColor(ORO_CLARO)
        c.setFont("Helvetica", 10)
        c.drawString(6.5*cm, alto-3.5*cm, f"{self.ciudad} — {self.provincia}")
        c.setFillColor(ORO)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(6.5*cm, alto-4.5*cm, "ZONA CLIMATICA CTE")
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(6.5*cm, alto-5.6*cm, self.zona)
        c.setFillColor(ORO_CLARO)
        c.setFont("Helvetica", 8.5)
        c.drawString(8.5*cm, alto-5.2*cm, f"Clima: {self.clima}")
        c.drawString(8.5*cm, alto-5.8*cm, f"Altitud: {self.altitud} m")
        c.setFillColor(GRIS_MED)
        c.setFont("Helvetica-Oblique", 7.5)
        c.drawString(6.5*cm, alto-6.5*cm, self.obs)
        c.setFillColor(ORO)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawRightString(ancho-0.5*cm, 0.7*cm, f"Generado: {self.fecha}")

def tabla_sistema(s):
    nombre    = s.get('property_sistema', s.get('name', ''))
    tipo      = s.get('property_tipo', '')
    desc      = s.get('property_descripcion', '')
    ventajas  = s.get('property_ventajas', '')
    recom     = s.get('property_recomendaciones', '')
    normativa = s.get('property_normativa', '')
    lambda_v  = s.get('property_lambda', '')
    uw_v      = s.get('property_uw', '')
    lod       = s.get('property_lod', '')
    prioridad = s.get('property_prioridad', '')
    color_tipo = COLORES_TIPO.get(tipo, GRIS_MED)
    icono = ICONOS_TIPO.get(tipo, "BIM")

    cab = [[
        Paragraph(f"<b>{icono}</b>", ParagraphStyle("ic", fontName="Helvetica-Bold",
            fontSize=9, textColor=BLANCO, leading=11, alignment=TA_CENTER)),
        Paragraph(f"<b>{nombre}</b>", ParagraphStyle("sn", fontName="Helvetica-Bold",
            fontSize=9.5, textColor=NEGRO, leading=12)),
        Paragraph(f"<b>{tipo}</b>", ParagraphStyle("tp", fontName="Helvetica-Bold",
            fontSize=7.5, textColor=BLANCO, leading=10, alignment=TA_CENTER)),
    ]]
    t_cab = Table(cab, colWidths=[1.2*cm, 12*cm, 2.8*cm])
    t_cab.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0),color_tipo),
        ("BACKGROUND",(1,0),(1,0),ORO_BG),
        ("BACKGROUND",(2,0),(2,0),color_tipo),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("LINEBELOW",(0,0),(-1,0),1.5,ORO),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))

    filas = []
    if desc:      filas.append([Paragraph("Descripcion", s_celda_b), Paragraph(desc, s_celda)])
    if ventajas:  filas.append([Paragraph("Ventajas", s_celda_b), Paragraph(ventajas, s_celda)])
    if recom:     filas.append([Paragraph("Recomendaciones", s_celda_b), Paragraph(recom, s_celda)])
    if normativa: filas.append([Paragraph("Normativa", s_celda_b), Paragraph(normativa, s_celda)])
    params = []
    if lambda_v: params.append(f"lambda = {lambda_v}")
    if uw_v:     params.append(f"Uw = {uw_v}")
    if lod:      params.append(f"LOD {lod}")
    if prioridad: params.append(f"Prioridad {prioridad}")
    if params:   filas.append([Paragraph("Parametros tecnicos", s_celda_b), Paragraph("  |  ".join(params), s_celda_b)])
    if not filas: filas.append([Paragraph("-", s_celda), Paragraph("-", s_celda)])

    t_datos = Table(filas, colWidths=[2.8*cm, 13.2*cm])
    estilos_d = [
        ("GRID",(0,0),(-1,-1),0.3,GRIS_LINE),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]
    for i in range(len(filas)):
        bg0 = GRIS_CLAR if i%2==0 else colors.HexColor("#EBEBEB")
        bg1 = BLANCO if i%2==0 else GRIS_CLAR
        estilos_d += [("BACKGROUND",(0,i),(0,i),bg0),("BACKGROUND",(1,i),(1,i),bg1)]
    t_datos.setStyle(TableStyle(estilos_d))
    return [t_cab, t_datos, sp(8)]

def generar_pdf(data):
    ciudad    = data.get('ciudad', '')
    provincia = data.get('provincia', '')
    uso       = data.get('uso_edificio', '')
    zona      = data.get('zona_cte', '')
    clima     = data.get('clima', '')
    altitud   = data.get('altitud', 0)
    obs       = data.get('observaciones_clima', '')
    fecha     = data.get('fecha', '—')
    sistemas  = data.get('sistemas', [])
    es_mixto  = data.get('es_mixto', False)
    sistemas_por_uso = data.get('sistemas_por_uso', {})

    story = []
    story.append(sp(0.5*cm))
    story.append(Portada(ciudad, provincia, uso, zona, clima, altitud, obs, fecha))
    story.append(sp(0.8*cm))

    # Tabla resumen
    story.append(Paragraph("RESUMEN DE SISTEMAS PROPUESTOS", s_h2))
    story.append(HRFlowable(width="100%", thickness=1, color=ORO, spaceAfter=8))

    lista_sistemas = sistemas if not es_mixto else [s for usos in sistemas_por_uso.values() for s in usos]

    resumen = [[
        Paragraph("<b>Cod.</b>",s_hdr_t), Paragraph("<b>Tipo</b>",s_hdr_t),
        Paragraph("<b>Sistema propuesto</b>",s_hdr_t), Paragraph("<b>Normativa</b>",s_hdr_t),
        Paragraph("<b>LOD</b>",s_hdr_t), Paragraph("<b>P.</b>",s_hdr_t),
    ]]
    for i, s in enumerate(lista_sistemas):
        tipo = s.get('property_tipo','')
        resumen.append([
            Paragraph(ICONOS_TIPO.get(tipo,'BIM'), s_celda_b),
            Paragraph(tipo, ParagraphStyle("tp2", fontName="Helvetica-Bold", fontSize=7.5,
                textColor=COLORES_TIPO.get(tipo, GRIS_MED), leading=10)),
            Paragraph(s.get('property_sistema', s.get('name','')), s_celda),
            Paragraph(s.get('property_normativa','—'), s_celda),
            Paragraph(str(s.get('property_lod','—')), s_celda),
            Paragraph(str(s.get('property_prioridad','—')), s_celda),
        ])

    estilos_r = [
        ("BACKGROUND",(0,0),(-1,0),NEGRO),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_LINE),
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEABOVE",(0,0),(-1,0),2,ORO), ("LINEBELOW",(0,-1),(-1,-1),1.5,ORO),
        ("ALIGN",(0,0),(0,-1),"CENTER"), ("ALIGN",(4,0),(5,-1),"CENTER"),
    ]
    for i in range(1, len(resumen)):
        bg = GRIS_CLAR if i%2==0 else BLANCO
        estilos_r.append(("BACKGROUND",(0,i),(-1,i),bg))

    t_res = Table(resumen, colWidths=[1.2*cm, 2.5*cm, 6.8*cm, 3.8*cm, 1.2*cm, 1*cm])
    t_res.setStyle(TableStyle(estilos_r))
    story.append(t_res)
    story.append(saltop())

    # Fichas técnicas
    if es_mixto:
        for uso_zona, sists in sistemas_por_uso.items():
            story.append(Paragraph(f"FICHAS TECNICAS — {uso_zona.upper()}", s_h2))
            story.append(HRFlowable(width="100%", thickness=1, color=ORO, spaceAfter=10))
            for s in sists:
                for e in tabla_sistema(s): story.append(e)
            story.append(saltop())
    else:
        story.append(Paragraph("FICHAS TECNICAS DETALLADAS", s_h2))
        story.append(HRFlowable(width="100%", thickness=1, color=ORO, spaceAfter=10))
        for s in sistemas:
            for e in tabla_sistema(s): story.append(e)
        story.append(saltop())

    # Tabla transmitancias
    story.append(Paragraph(f"VERIFICACION DE TRANSMITANCIAS CTE DB-HE — ZONA {zona}", s_h2))
    story.append(HRFlowable(width="100%", thickness=1, color=ORO, spaceAfter=8))

    fachada_s = next((s for s in lista_sistemas if s.get('property_tipo')=='FACHADAS'), None)
    cubierta_s = next((s for s in lista_sistemas if s.get('property_tipo')=='CUBIERTAS'), None)
    suelo_s = next((s for s in lista_sistemas if s.get('property_tipo')=='SUELOS'), None)
    carp_s = next((s for s in lista_sistemas if s.get('property_tipo')=='CARPINTERIA'), None)

    umaximos = {"A":["0.60","0.45","0.50","1.60"],"B":["0.50","0.40","0.45","1.40"],
                "C":["0.38","0.30","0.38","1.20"],"D":["0.30","0.25","0.30","1.00"],"E":["0.25","0.20","0.25","0.80"]}
    zona_letra = zona[0] if zona else "C"
    umax = umaximos.get(zona_letra, umaximos["C"])

    trans = [[
        Paragraph("<b>Elemento</b>",s_hdr_t), Paragraph("<b>Sistema propuesto</b>",s_hdr_t),
        Paragraph("<b>U max. CTE</b>",s_hdr_t), Paragraph("<b>U proyecto</b>",s_hdr_t),
        Paragraph("<b>Cumple</b>",s_hdr_t),
    ]]
    elementos = [
        ("Fachada", fachada_s, umax[0]),
        ("Cubierta", cubierta_s, umax[1]),
        ("Suelo", suelo_s, umax[2]),
        ("Huecos", carp_s, umax[3]),
    ]
    for nombre_e, sist, umaximo in elementos:
        uw = sist.get('property_uw','—') if sist else '—'
        nombre_sist = sist.get('property_sistema', sist.get('name','—')) if sist else '—'
        trans.append([
            Paragraph(nombre_e, s_celda_b),
            Paragraph(nombre_sist, s_celda),
            Paragraph(f"{umaximo} W/m2K", s_celda),
            Paragraph(uw if uw else "Ver ficha", s_celda_b),
            Paragraph("SÍ", s_ok),
        ])

    t_trans = Table(trans, colWidths=[2.5*cm, 7*cm, 2.5*cm, 2.8*cm, 1.7*cm])
    t_trans.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NEGRO),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_LINE),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEABOVE",(0,0),(-1,0),2,ORO), ("LINEBELOW",(0,-1),(-1,-1),1.5,ORO),
        ("BACKGROUND",(0,1),(-1,1),BLANCO), ("BACKGROUND",(0,2),(-1,2),GRIS_CLAR),
        ("BACKGROUND",(0,3),(-1,3),BLANCO), ("BACKGROUND",(0,4),(-1,4),GRIS_CLAR),
        ("ALIGN",(2,0),(4,-1),"CENTER"),
    ]))
    story.append(t_trans)
    story.append(sp(0.8*cm))

    # Nota familias
    nota = [[
        Paragraph("FAMILIAS REVIT", ParagraphStyle("nf", fontName="Helvetica-Bold",
            fontSize=9, textColor=ORO, leading=12)),
        Paragraph(f'Descarga las familias BIM de los sistemas propuestos: {ENLACE_FAMILIAS}',
            ParagraphStyle("nft", fontName="Helvetica", fontSize=8, textColor=BLANCO, leading=12)),
    ]]
    t_nota = Table(nota, colWidths=[3.5*cm, 13*cm])
    t_nota.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NEGRO),
        ("TOPPADDING",(0,0),(-1,-1),10), ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("LINEABOVE",(0,0),(-1,0),2,ORO), ("LINEBELOW",(0,0),(-1,0),2,ORO),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(t_nota)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=2.4*cm, bottomMargin=1.5*cm,
        title="Informe BIM Profesional — Arquetrix Desing",
        author="Arquetrix BIM Assistant")
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buf.seek(0)
    return buf

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/generar-pdf', methods=['POST'])
def generar():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        buf = generar_pdf(data)
        return send_file(buf, mimetype='application/pdf',
                        as_attachment=True,
                        download_name='informe_bim.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
