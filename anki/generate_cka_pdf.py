
import os
import sys
import json
import html
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Define CKA Sections
SECTIONS = {
    "Cluster Architecture, Installation & Configuration": [
        "etcd", "kubeadm", "upgrade", "backup", "restore", "rbac", "role", "clusterrole",
        "control plane", "api server", "scheduler", "controller manager", "cloud-init", "version", "architecture"
    ],
    "Workloads & Scheduling": [
        "pod", "deployment", "replicaset", "daemonset", "statefulset", "job", "cronjob",
        "scale", "rollout", "update", "image", "init container", "sidecar", "probe",
        "liveness", "readiness", "limit", "request", "affinity", "taint", "toleration",
        "node selector", "static pod", "manifest", "resource", "priority class"
    ],
    "Services & Networking": [
        "service", "ingress", "network policy", "cni", "dns", "coredns", "nodeport",
        "clusterip", "loadbalancer", "networking", "iptables", "kube-proxy", "gateway",
        "endpoint", "calico", "flannel", "weave", "netpol"
    ],
    "Storage": [
        "pv", "pvc", "persistent volume", "storage class", "sc", "volume", "mount", "claim",
        "csi", "storage", "nfs", "hostpath", "emptydir", "access mode"
    ],
    "Troubleshooting": [
        "debug", "log", "troubleshoot", "failure", "monitor", "event", "jsonpath", "top",
        "drain", "uncordon", "fix", "issue", "error", "crashloopbackoff", "imagepullbackoff",
        "notready", "pending", "status", "journalctl", "systemctl", "crictl", "exec"
    ]
}

def categorize_card(question, answer, notes):
    content = (question + " " + answer + " " + notes).lower()
    
    # Check sections in specific order (some keywords might overlap, order matters for precedence)
    # Troubleshooting often has overlapping terms, but usually specific context.
    
    scores = {section: 0 for section in SECTIONS}
    
    for section, keywords in SECTIONS.items():
        for keyword in keywords:
            if keyword in content:
                scores[section] += 1
    
    # If no matches, return "Miscellaneous"
    if max(scores.values()) == 0:
        return "Miscellaneous"
    
    # Return the section with the highest score
    return max(scores, key=scores.get)

def create_pdf(input_file, output_file):
    print(f"Reading from {input_file}...")
    
    grouped_cards = {section: [] for section in SECTIONS}
    grouped_cards["Miscellaneous"] = []
    
    # Check if input is JSON (consolidated data) or TXT (legacy)
    if input_file.endswith(".json"):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                question = item.get("question", "")
                answer = item.get("command", "")
                notes = item.get("notes", "")
                
                # Use pre-defined section if available, else categorize
                if "section" in item:
                    section = item["section"]
                else:
                    section = categorize_card(question, answer, notes)
                    
                if section not in grouped_cards:
                     grouped_cards[section] = []
                     
                grouped_cards[section].append((question, answer, notes))
                
        except Exception as e:
             print(f"Error reading JSON: {e}")
             return
    else:
        # Legacy TXT parsing
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                    
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                question = parts[0]
                answer = parts[1]
                notes = parts[2] if len(parts) > 2 else ""
                
                section = categorize_card(question, answer, notes)
                grouped_cards[section].append((question, answer, notes))
                
        except FileNotFoundError:
            print(f"Error: File {input_file} not found.")
            return

    print("Generating PDF...")
    doc = SimpleDocTemplate(output_file, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1, # Center
        spaceAfter=20
    )
    elements.append(Paragraph("CKA Certification Flashcards", title_style))
    elements.append(Spacer(1, 12))

    # Cell Styles
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12
    )

    # Process each section
    seq_counter = 1
    
    # Sort sections in logical CKA order or alphabetical?
    # CKA Order: Cluster Arch -> Workloads -> Services -> Storage -> Troubleshoot
    order = [
        "Cluster Architecture, Installation & Configuration",
        "Workloads & Scheduling",
        "Services & Networking",
        "Storage",
        "Troubleshooting",
        "Helm & Kustomize",
        "Miscellaneous"
    ]
    
    active_sections = []
    
    for section in order:
        if section not in active_sections and section in grouped_cards:
             active_sections.append(section)
        
    # Add any others that might have appeared
    for s in grouped_cards.keys():
        if s not in active_sections:
            active_sections.append(s)
    
    for section in active_sections:
        cards = grouped_cards.get(section, [])
        if not cards:
            continue
            
        # Section Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        )
        elements.append(Paragraph(section, header_style))
        
        # Table Data
        # Header Row
        table_data = [['#', 'Question', 'Answer', 'Notes']]
        
        for q, a, n in cards:
            # Escape HTML characters to prevent reportlab parser errors
            q = html.escape(str(q))
            a = html.escape(str(a))
            n = html.escape(str(n))
            
            # Wrap text in Paragraphs to allow multi-line cells
            p_seq = Paragraph(str(seq_counter), cell_style)
            p_q = Paragraph(q, cell_style)
            p_a = Paragraph(a, cell_style)
            p_n = Paragraph(n, cell_style)
            
            table_data.append([p_seq, p_q, p_a, p_n])
            seq_counter += 1
            
        # Create Table
        # Column widths: Seq: 5%, Q: 30%, A: 35%, N: 30%
        # A4 Landscape width approx 11.7 inch. Margins 30pt ~ 0.4 inch each side.
        # Available width approx 10.8 inch.
        col_widths = [0.4 * inch, 3.2 * inch, 3.7 * inch, 3.2 * inch]
        
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table Style
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))

    try:
        doc.build(elements)
        print(f"PDF generated successfully: {output_file}")
    except Exception as e:
        print(f"Failed to generate PDF: {e}")

if __name__ == "__main__":
    # Prefer finetuned JSON
    base_path = "/Users/sanjeevmurthy/le/repos/le-utilities/anki"
    json_input = os.path.join(base_path, "finetuned_flashcards.json")
    
    if os.path.exists(json_input):
        input_filename = json_input
        print(f"Using finetuned data: {input_filename}")
    elif os.path.exists(os.path.join(base_path, "consolidated_commands.json")):
         input_filename = os.path.join(base_path, "consolidated_commands.json")
    else:
        input_filename = "CKA Prep.txt"
    
    output_filename = os.path.join(base_path, "CKA_Prep_Flashcards_Finetuned.pdf")
        
    create_pdf(input_filename, output_filename)
