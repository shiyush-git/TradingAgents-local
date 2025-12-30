
import os
from pathlib import Path
import markdown
from langchain_core.messages import HumanMessage
import sys

def generate_chinese_pdf(llm, ticker, date_str, results_dir_base="results"):
    """
    Translates markdown reports to Chinese, combines them, and generates a PDF.
    """
    try:
        from weasyprint import HTML, CSS
    except OSError as e:
        print(f"Error: WeasyPrint failed to load external libraries (GTK3). Please ensure GTK3 is installed and in your PATH. Details: {e}")
        return
    except ImportError as e:
        print(f"Error: WeasyPrint not installed. Details: {e}")
        return
    base_path = Path(results_dir_base) / ticker / date_str
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    # Files to process in specific order
    files_to_process = [
        "1_market_analysis.md",
        "2_news_analysis.md",
        "3_social_sentiment.md",
        "4_fundamentals.md",
        "5_investment_debate.md",
        "6_risk_debate.md",
        "7_investment_plan.md",
        "8_trader_decision.md",
        "9_final_decision.md"
    ]

    full_html_content = ""
    print(f"Starting translation and PDF generation for {ticker} on {date_str}...")

    # CSS for the PDF
    css_content = """
    @font-face {
        font-family: 'Microsoft YaHei';
        src: local('Microsoft YaHei'), local('msyh');
    }
    body {
        font-family: 'Microsoft YaHei', sans-serif;
        padding: 40px;
        font-size: 14px;
        line-height: 1.6;
        color: #333;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: bold;
    }
    h1 { font-size: 28px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    h2 { font-size: 24px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
    h3 { font-size: 20px; }
    p { margin-bottom: 16px; text-align: justify; }
    ul, ol { margin-bottom: 16px; padding-left: 24px; }
    li { margin-bottom: 8px; }
    code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-family: Consolas, monospace; }
    pre { background-color: #f8f9fa; padding: 16px; border-radius: 4px; overflow-x: auto; }
    blockquote { border-left: 4px solid #dfe6e9; margin: 0; padding-left: 16px; color: #636e72; }
    hr { margin: 40px 0; border: 0; border-top: 1px solid #e1e4e8; }
    .section-break { page-break-before: always; }
    .report-title { text-align: center; margin-bottom: 60px; }
    
    /* Table Styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
    }
    th, td {
        border: 1px solid #dfe6e9;
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background-color: #f8f9fa;
        font-weight: bold;
        color: #2c3e50;
    }
    tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    """

    # Add Title Page Content
    full_html_content += f"""
    <div class="report-title">
        <h1>{ticker} 投资分析报告</h1>
        <h3>日期: {date_str}</h3>
    </div>
    """

    import re

    for filename in files_to_process:
        file_path = base_path / filename
        cn_filename = filename.replace(".md", "_CN.md")
        cn_file_path = base_path / cn_filename
        
        translated_content = ""

        # Check if translation exists
        if cn_file_path.exists():
            try:
                with open(cn_file_path, "r", encoding="utf-8") as f:
                    existing = f.read()
                # Check for at least one Chinese character to verify it's a valid translation
                if re.search(r'[\u4e00-\u9fff]', existing):
                    print(f"Found existing translation for {filename}, skipping LLM call.")
                    translated_content = existing
            except Exception as e:
                print(f"Error reading existing translation {cn_filename}: {e}")

        if not translated_content and file_path.exists():
            print(f"Processing {filename}...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Translate
                prompt = f"""You are a professional financial translator. 
                Translate the following markdown content into Simplified Chinese (简体中文). 
                Rules:
                1. Maintain the markdown formatting structure (headers, lists, bolding, etc.) exactly.
                2. Do not add any preamble (like "Here is the translation") or postscript.
                3. Keep financial terms accurate.
                4. For the "Investment Debate" and "Risk Debate" sections, ensure the dialogue format is preserved.
                
                Content to translate:
                {content}
                """
                
                response = llm.invoke([HumanMessage(content=prompt)])
                translated_content = response.content
                
                # Save the translation for future runs
                try:
                    with open(cn_file_path, "w", encoding="utf-8") as f:
                        f.write(translated_content)
                    print(f"Saved translation to {cn_filename}")
                except Exception as save_err:
                    print(f"Warning: Could not save translation to {cn_filename}: {save_err}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

        if translated_content:
            # Convert to HTML
            html_section = markdown.markdown(translated_content, extensions=['tables'])
            
            # Add a section break and the content
            full_html_content += f"<div class='section-break'></div>\n"
            full_html_content += f"<div class='section'>\n{html_section}\n</div>\n"

    # Generate final HTML
    final_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>{ticker} Analysis Report</title>
    </head>
    <body>
        {full_html_content}
    </body>
    </html>
    """

    output_pdf_path = base_path / f"0_{ticker}_{date_str}_Full_Report_CN.pdf"
    
    try:
        # Use WeasyPrint to generate PDF
        print(f"Generating PDF at {output_pdf_path}...")
        html = HTML(string=final_html)
        css = CSS(string=css_content)
        html.write_pdf(target=str(output_pdf_path), stylesheets=[css])
        print(f"PDF generated successfully: {output_pdf_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
