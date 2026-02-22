import markdown
import os
import sys
import subprocess

def convert_md_to_pdf(source_md, output_pdf):
    print(f"Reading {source_md}...")
    
    # 1. Read Markdown
    try:
        with open(source_md, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"Error: Source file not found: {source_md}")
        return

    # 2. Convert to HTML
    html_content = markdown.markdown(md_text, extensions=['fenced_code', 'tables', 'sane_lists'])

    # 3. Create Styled HTML
    styled_html = f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            font-size: 20px;
            color: #2c3e50;
            border-bottom: 2px solid #eaecef;
            padding-bottom: 10px;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }}
        h2 {{
            font-size: 18px;
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 5px;
            font-weight: 600;
        }}
        h3 {{
            font-size: 16px;
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: "Courier New", Courier, monospace;
            font-size: 13px;
            overflow-x: auto;
        }}
        code {{
            background-color: #f8f9fa;
            font-family: "Courier New", Courier, monospace;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.9em;
            border: 1px solid #e9ecef;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        blockquote {{
            border-left: 4px solid #ccc;
            margin: 0 0 15px 0;
            padding-left: 15px;
            color: #666;
            font-style: italic;
        }}
        ul, ol {{
            margin-bottom: 15px;
            padding-left: 30px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        /* Print Styles */
        @media print {{
            body {{
                width: 100%;
                margin: 0;
                padding: 0;
            }}
            @page {{
                margin: 1in;
            }}
        }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # 4. Save intermediate HTML
    temp_html = source_md.replace(".md", ".html")
    with open(temp_html, "w", encoding='utf-8') as f:
        f.write(styled_html)
    print(f"Created temporary HTML: {temp_html}")

    # 5. Convert to PDF using Headless Chrome
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={output_pdf}",
        temp_html
    ]
    
    print("Generating PDF with Chrome...")
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        print(f"PDF generated successfully: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"Error running Chrome: {e}")
    except FileNotFoundError:
        print(f"Chrome not found at {chrome_path}. Please verify installation.")
    
    # Optional: cleanup
    # os.remove(temp_html)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Default filenames
    source_file = "Part 2 50 Questions.md"
    output_file = "Part_2_50_Questions.pdf"
    
    # Allow arguments
    if len(sys.argv) > 1:
        source_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    # Handle paths relative to script
    source_path = os.path.join(current_dir, source_file)
    output_path = os.path.join(current_dir, output_file)

    convert_md_to_pdf(source_path, output_path)
