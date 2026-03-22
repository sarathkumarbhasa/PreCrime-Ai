import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def get_level_color(score):
    if score >= 81: return colors.HexColor('#ffe0e0') # light red
    if score >= 66: return colors.HexColor('#fff0e0') # light orange
    if score >= 41: return colors.HexColor('#fffde0') # light yellow
    return colors.HexColor('#f0fff0') # light green

def get_level_name(score):
    if score >= 81: return "CRITICAL"
    if score >= 66: return "HIGH"
    if score >= 41: return "WATCH"
    return "NORMAL"

def generate_report(entities, threats, personas, timeline):
    VALID_ENTITIES = {f"E{str(i).zfill(3)}" for i in range(1,21)}
    entities = [e for e in entities if e.get('entity_id') in VALID_ENTITIES]
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#cc0000'),
        alignment=1,
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=15
    )
    
    normal_style = styles['Normal']
    
    elements = []
    
    # --- PAGE 1: COVER PAGE ---
    elements.append(Spacer(1, 5*cm))
    elements.append(Paragraph("🔴 [CLASSIFIED] INTELLIGENCE BRIEF", title_style))
    elements.append(Paragraph("PRECRIME AI<br/>Predictive Threat Assessment", ParagraphStyle('Sub', parent=title_style, fontSize=18, textColor=colors.black)))
    elements.append(Spacer(1, 3*cm))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = f"PCA-{datetime.now().strftime('%Y%m%d%H%M')}"
    total_threats = len([e for e in entities if e.get('score', 0) >= 66])
    
    cover_data = [
        ["Report ID:", report_id],
        ["Generated:", timestamp],
        ["Classification:", "RESTRICTED"],
        ["Total Threats Detected:", str(total_threats)],
        ["Analysis Period:", "Last 7 Days"]
    ]
    t = Table(cover_data, colWidths=[6*cm, 8*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    
    # --- PAGE 2: EXECUTIVE SUMMARY ---
    elements.append(Paragraph("EXECUTIVE SUMMARY", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    crit_count = len([e for e in entities if e['score'] >= 81])
    high_count = len([e for e in entities if 66 <= e['score'] <= 80])
    watch_count = len([e for e in entities if 41 <= e['score'] <= 65])
    norm_count = len([e for e in entities if e['score'] <= 40])
    
    total_entities_filtered = len([e for e in entities if e.get('entity_id') in VALID_ENTITIES])
    summary_data = [
        ["Total entities analyzed", str(total_entities_filtered)],
        ["Critical threats count", str(crit_count)],
        ["High threats count", str(high_count)],
        ["Watch level count", str(watch_count)],
        ["Normal entities count", str(norm_count)]
    ]
    t2 = Table(summary_data, colWidths=[8*cm, 4*cm])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#1a1a2e')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 1*cm))
    
    elements.append(Paragraph("Top 3 most dangerous entities:", styles['Heading3']))
    sorted_entities = sorted(entities, key=lambda x: x['score'], reverse=True)[:3]
    for ent in sorted_entities:
        elements.append(Paragraph(f"- {ent['entity_id']}: {min(ent['score'], 95)}/100", normal_style))
        
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("Recommended immediate action:", styles['Heading3']))
    elements.append(Paragraph("Deploy surveillance assets to monitor CRITICAL entities and investigate identified geo-convergence zones.", normal_style))
    elements.append(PageBreak())
    
    # --- PAGE 3: THREAT FORECAST ---
    elements.append(Paragraph("THREAT FORECAST", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    for i, t in enumerate(threats):
        cluster_data = [
            ["CLUSTER ID:", t.get('cluster_id', f"#{i+1}")],
            ["THREAT LEVEL:", t.get('threat_level', 'UNKNOWN')],
            ["PRIMARY ENTITY:", t.get('primary_entity', 'Unknown')],
            ["MEMBERS:", str(t.get('member_count', 0)) + " entities"],
            ["ACTIVATION WINDOW:", t.get('activation_window', 'Unknown')],
            ["CONFIDENCE:", f"{min(t.get('confidence', 0), 92.0):.1f}%"],
            ["ACTIVE SIGNALS:", f"{t.get('active_signals', 0)}/5"],
            ["LAST GEO-CONVERGENCE:", t.get('last_convergence', 'N/A')]
        ]
        ct = Table(cluster_data, colWidths=[5*cm, 10*cm])
        ct.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f0f5')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(ct)
        elements.append(Spacer(1, 0.5*cm))
    
    elements.append(PageBreak())
    
    # --- PAGE 4: ENTITY HEAT SCORE TABLE ---
    elements.append(Paragraph("ENTITY HEAT SCORE TABLE", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    # Sync archetypes from persona map BEFORE building the table
    for entity in entities:
        eid = entity.get('entity_id')
        if eid in personas:
            label = personas[eid].get('archetype_label', 'Unknown')
            entity['archetype'] = label.replace("The ", "").strip()

    table_data = [["Entity ID", "Heat Score", "Level", "Archetype", "Triggered Signals", "Status"]]
    for e in sorted(entities, key=lambda x: x['score'], reverse=True):
        score = min(e['score'], 95)
        level = get_level_name(score)
        arch = e.get('archetype', 'Unknown')
        sigs = str(len(e.get('signals', [])))
        status = "Active"
        
        table_data.append([e['entity_id'], str(score), level, arch, sigs, status])
        
    ht = Table(table_data, colWidths=[2.5*cm, 2*cm, 2.5*cm, 3.5*cm, 3*cm, 2*cm])
    
    # Style logic based on rows
    ts = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 5),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]
    
    for row_idx, e in enumerate(sorted(entities, key=lambda x: x['score'], reverse=True), start=1):
        bg_color = get_level_color(e['score'])
        ts.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color))
        
    ht.setStyle(TableStyle(ts))
    elements.append(ht)
    elements.append(PageBreak())
    
    # --- PAGE 5: PERSONA PROFILES ---
    elements.append(Paragraph("PERSONA PROFILES (HIGH/CRITICAL)", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    target_entities = [e for e in entities if e['score'] >= 66]
    for e in sorted(target_entities, key=lambda x: x['score'], reverse=True):
        eid = e['entity_id']
        score = min(e['score'], 95)
        level = get_level_name(score)
        prof = personas.get(eid, {})
        
        arch = prof.get('archetype_label', 'UNKNOWN')
        conf = prof.get('confidence_statement', 'N/A')
        summ = prof.get('behavioral_summary', 'Behavioral profile pending analysis.')
        risk = prof.get('risk_assessment', 'Unknown')
        rec = prof.get('recommended_action', 'Unknown')
        centrality = prof.get('centrality', 0.0)
        
        box_elements = []
        
        box_elements.append(Paragraph(f"<b>{eid} — {arch.upper()}</b>", styles['Heading3']))
        box_elements.append(Paragraph(f"Heat Score: {score} | Centrality: {centrality:.2f} | Priority: {level}", normal_style))
        box_elements.append(Spacer(1, 0.4*cm))
        
        box_elements.append(Paragraph("<b>CONFIDENCE:</b>", normal_style))
        box_elements.append(Paragraph(conf, normal_style))
        box_elements.append(Spacer(1, 0.3*cm))
        
        box_elements.append(Paragraph("<b>BEHAVIORAL PROFILE:</b>", normal_style))
        box_elements.append(Paragraph(summ, normal_style))
        box_elements.append(Spacer(1, 0.3*cm))
        
        box_elements.append(Paragraph("<b>RISK ASSESSMENT:</b>", normal_style))
        box_elements.append(Paragraph(risk, normal_style))
        box_elements.append(Spacer(1, 0.3*cm))
        
        box_elements.append(Paragraph("<b>RECOMMENDED ACTION:</b>", normal_style))
        box_elements.append(Paragraph(rec, normal_style))
        box_elements.append(Spacer(1, 0.3*cm))
        
        box_elements.append(Paragraph("<b>Key Signals:</b>", normal_style))
        
        all_possible = ["Call frequency spike", "Unusual hours activity", "Location convergence", "Transaction micro-splits", "New burner contact"]
        triggered = e.get('signals', [])
        for sig in all_possible:
            if sig in triggered:
                box_elements.append(Paragraph(f"✓ {sig}", normal_style))
            else:
                box_elements.append(Paragraph(f"✗ {sig}", normal_style))
                
        card_table = Table([[box_elements]], colWidths=[16.5*cm])
        card_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1a1a2e')),
            ('PADDING', (0,0), (-1,-1), 15),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f9fc')),
        ]))
        
        elements.append(card_table)
        elements.append(Spacer(1, 0.8*cm))

    elements.append(PageBreak())
    
    # --- PAGE 6: TIMELINE OF EVENTS ---
    elements.append(Paragraph("TIMELINE OF EVENTS", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    tl_data = [["Timestamp", "Entity", "Event Type", "Source", "Severity", "Description"]]
    
    seen = set()
    unique_events = []
    for event in timeline:
        key = f"{event.get('timestamp')}_{event.get('entity')}_{event.get('desc')}"
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    timeline = unique_events
    
    # Timeline is passed in sorted order
    # Ensure it fits on page, so we truncate desc and length
    for event in timeline[:30]:
        t_str = str(event.get('timestamp', ''))[:16].replace('T', ' ')
        e_id = str(event.get('entity', ''))
        e_type = str(event.get('type', ''))
        src = str(event.get('source', ''))
        sev = str(event.get('severity', ''))
        
        desc = str(event.get('desc', ''))
        desc = desc[:30] + '...' if len(desc) > 30 else desc
        
        tl_data.append([t_str, e_id, e_type, src, sev, desc])
        
    tt = Table(tl_data, colWidths=[3.5*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 5*cm])
    tt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(tt)
    elements.append(PageBreak())
    
    # --- PAGE 7: INVESTIGATOR NOTES & FOOTER ---
    elements.append(Paragraph("INVESTIGATOR NOTES", header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=15))
    
    notes = """
    <b>Data sources used:</b> Telecom CDR records, Encrypted Chat metadata, Financial Ledgers, and GPS tracking logs.<br/><br/>
    <b>Analysis methodology:</b> Network graph analysis mapped via D3-compliant structuring, augmented with heuristic behavioral baselining for anomalous spike detection. Clusters are evaluated against historical syndicate profiles.<br/><br/>
    <b>Disclaimer:</b> Information contained herein is predictive and probabilistic. Ground-truth validation via field operations is advised before tactical deployment.<br/><br/>
    <font color='#cc0000'><b>Generated by PRECRIME AI — For Law Enforcement Use Only</b></font>
    """
    elements.append(Paragraph(notes, normal_style))
    
    # Custom canvas to add header/footer on every page
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setStrokeColor(colors.grey)
        
        # Header
        canvas.drawString(2*cm, 28.5*cm, "PRECRIME AI | RESTRICTED")
        canvas.line(2*cm, 28.3*cm, 19*cm, 28.3*cm)
        
        # Footer
        canvas.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
        canvas.drawString(2*cm, 1*cm, f"Report ID: {report_id}")
        canvas.drawRightString(19*cm, 1*cm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    
    return pdf_buffer.getvalue()
