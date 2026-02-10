from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

def build_pdf(path, summary, keywords, transcript, images):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    content = []

    content.append(Paragraph("Video Notes", styles["Title"]))

    content.append(Paragraph("Summary", styles["Heading2"]))
    for s in summary:
        content.append(Paragraph("• " + s, styles["Normal"]))

    content.append(Paragraph("Key Concepts", styles["Heading2"]))
    content.append(Paragraph(", ".join(keywords), styles["Normal"]))

    content.append(Paragraph("Transcript", styles["Heading2"]))
    for line in transcript:
        content.append(Paragraph(line, styles["Normal"]))

    content.append(Paragraph("Visual Highlights", styles["Heading2"]))
    for img in images:
        content.append(Image(img, width=300, height=180))

    doc.build(content)
