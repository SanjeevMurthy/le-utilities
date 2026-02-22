#!/usr/bin/env python3
"""
Instagram Excel Data Analyzer

This script analyzes Excel files containing Instagram page data.
It identifies unique Instagram links, detects duplicates across files,
and generates comprehensive statistics.
"""

import pandas as pd
import re
import os
from pathlib import Path
from collections import defaultdict
import json


def extract_instagram_links(df: pd.DataFrame) -> list:
    """
    Extract Instagram links from a DataFrame.
    Searches all columns for Instagram URLs.
    """
    instagram_pattern = r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?'
    links = []
    
    for col in df.columns:
        for value in df[col].dropna():
            value_str = str(value)
            matches = re.findall(instagram_pattern, value_str, re.IGNORECASE)
            for match in matches:
                # Normalize the link
                normalized = f"https://www.instagram.com/{match.lower().rstrip('/')}"
                links.append(normalized)
    
    return links


def analyze_excel_file(filepath: str) -> dict:
    """
    Analyze a single Excel file and return statistics.
    """
    result = {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'sheets': [],
        'total_rows': 0,
        'total_columns': 0,
        'column_names': [],
        'instagram_links': [],
        'unique_instagram_links': [],
        'duplicate_links_within_file': [],
        'data_sample': None,
        'data_types': {}
    }
    
    try:
        # Read all sheets
        xl = pd.ExcelFile(filepath)
        all_links = []
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            sheet_info = {
                'name': sheet_name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
            result['sheets'].append(sheet_info)
            result['total_rows'] += len(df)
            result['total_columns'] = max(result['total_columns'], len(df.columns))
            
            if not result['column_names']:
                result['column_names'] = list(df.columns)
                result['data_types'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
                # Get first few rows as sample
                result['data_sample'] = df.head(3).to_dict('records')
            
            # Extract Instagram links
            links = extract_instagram_links(df)
            all_links.extend(links)
        
        result['instagram_links'] = all_links
        result['unique_instagram_links'] = list(set(all_links))
        
        # Find duplicates within file
        link_counts = defaultdict(int)
        for link in all_links:
            link_counts[link] += 1
        result['duplicate_links_within_file'] = [
            {'link': link, 'count': count} 
            for link, count in link_counts.items() 
            if count > 1
        ]
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def find_duplicates_across_files(file_analyses: list) -> dict:
    """
    Find Instagram links that appear in multiple files.
    """
    link_to_files = defaultdict(list)
    
    for analysis in file_analyses:
        for link in analysis['unique_instagram_links']:
            link_to_files[link].append(analysis['filename'])
    
    duplicates = {
        link: files 
        for link, files in link_to_files.items() 
        if len(files) > 1
    }
    
    return duplicates


def generate_report(file_analyses: list, cross_file_duplicates: dict, output_path: str):
    """
    Generate a comprehensive markdown report.
    """
    report = []
    report.append("# Instagram Excel Files Analysis Report\n")
    report.append(f"*Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Summary
    report.append("## Executive Summary\n")
    total_files = len(file_analyses)
    total_rows = sum(a['total_rows'] for a in file_analyses)
    total_links = sum(len(a['instagram_links']) for a in file_analyses)
    all_unique_links = set()
    for a in file_analyses:
        all_unique_links.update(a['unique_instagram_links'])
    
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Files Analyzed | {total_files} |")
    report.append(f"| Total Data Rows | {total_rows} |")
    report.append(f"| Total Instagram Links Found | {total_links} |")
    report.append(f"| Unique Instagram Pages (Global) | {len(all_unique_links)} |")
    report.append(f"| Cross-File Duplicates | {len(cross_file_duplicates)} |")
    report.append("")
    
    # File Details
    report.append("## Detailed File Analysis\n")
    
    for analysis in file_analyses:
        report.append(f"### 📁 {analysis['filename']}\n")
        report.append(f"**File Path:** `{analysis['filepath']}`\n")
        
        if 'error' in analysis:
            report.append(f"> [!WARNING]\n> Error reading file: {analysis['error']}\n")
            continue
        
        report.append(f"| Property | Value |")
        report.append(f"|----------|-------|")
        report.append(f"| Sheets | {len(analysis['sheets'])} |")
        report.append(f"| Total Rows | {analysis['total_rows']} |")
        report.append(f"| Total Columns | {analysis['total_columns']} |")
        report.append(f"| Instagram Links (Total) | {len(analysis['instagram_links'])} |")
        report.append(f"| Unique Instagram Pages | {len(analysis['unique_instagram_links'])} |")
        report.append(f"| Internal Duplicates | {len(analysis['duplicate_links_within_file'])} |")
        report.append("")
        
        # Column Information
        report.append("**Columns:**\n")
        for col in analysis['column_names']:
            dtype = analysis['data_types'].get(col, 'unknown')
            report.append(f"- `{col}` ({dtype})")
        report.append("")
        
        # Sheet Information
        if len(analysis['sheets']) > 1:
            report.append("**Sheet Details:**\n")
            for sheet in analysis['sheets']:
                report.append(f"- **{sheet['name']}**: {sheet['rows']} rows, {sheet['columns']} columns")
            report.append("")
        
        # Sample Data
        if analysis['data_sample']:
            report.append("**Data Sample (First 3 rows):**\n")
            report.append("```json")
            report.append(json.dumps(analysis['data_sample'], indent=2, default=str))
            report.append("```\n")
        
        # Internal Duplicates
        if analysis['duplicate_links_within_file']:
            report.append("**Duplicate Links Within File:**\n")
            for dup in analysis['duplicate_links_within_file'][:10]:
                report.append(f"- {dup['link']} (appears {dup['count']} times)")
            if len(analysis['duplicate_links_within_file']) > 10:
                report.append(f"- ... and {len(analysis['duplicate_links_within_file']) - 10} more")
            report.append("")
    
    # Cross-File Duplicates
    report.append("## Cross-File Duplicate Analysis\n")
    if cross_file_duplicates:
        report.append(f"Found **{len(cross_file_duplicates)}** Instagram pages appearing in multiple files:\n")
        report.append("| Instagram Page | Files |")
        report.append("|----------------|-------|")
        for link, files in sorted(cross_file_duplicates.items()):
            files_str = ", ".join(files)
            report.append(f"| {link} | {files_str} |")
        report.append("")
    else:
        report.append("> [!NOTE]\n> No duplicate Instagram pages found across files.\n")
    
    # Insights
    report.append("## Key Insights\n")
    
    # Calculate insights
    insights = []
    
    # Insight 1: File with most pages
    if file_analyses:
        max_file = max(file_analyses, key=lambda x: len(x.get('unique_instagram_links', [])))
        insights.append(f"1. **Largest Dataset**: `{max_file['filename']}` contains the most unique Instagram pages ({len(max_file['unique_instagram_links'])} pages)")
    
    # Insight 2: Duplicate rate
    if total_links > 0:
        dup_rate = (1 - len(all_unique_links) / total_links) * 100
        insights.append(f"2. **Duplicate Rate**: {dup_rate:.1f}% of all links are duplicates (internal + cross-file)")
    
    # Insight 3: Cross-file overlap
    if cross_file_duplicates:
        overlap_pct = len(cross_file_duplicates) / len(all_unique_links) * 100 if all_unique_links else 0
        insights.append(f"3. **Cross-File Overlap**: {overlap_pct:.1f}% of unique pages appear in multiple files")
    
    # Insight 4: Data coverage
    insights.append(f"4. **Total Coverage**: Combined dataset covers **{len(all_unique_links)}** unique Instagram creator pages")
    
    for insight in insights:
        report.append(insight)
    report.append("")
    
    # Potential Uses
    report.append("## Potential Data Uses\n")
    report.append("Based on the data structure, this dataset can be used for:\n")
    report.append("- **Influencer Discovery**: Finding Instagram creators in specific niches")
    report.append("- **Competitive Analysis**: Understanding top performing pages")
    report.append("- **Outreach Campaigns**: Building contact lists for marketing")
    report.append("- **Trend Analysis**: Identifying patterns across creator pages")
    report.append("- **Audience Research**: Understanding page categories and metrics\n")
    
    # All Unique Links
    report.append("## Complete List of Unique Instagram Pages\n")
    report.append(f"Total: **{len(all_unique_links)}** unique pages\n")
    report.append("<details>")
    report.append("<summary>Click to expand full list</summary>\n")
    for link in sorted(all_unique_links):
        report.append(f"- {link}")
    report.append("</details>\n")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    return '\n'.join(report)


def main():
    """Main function to run the analysis."""
    # Set paths
    files_dir = Path(__file__).parent / "files"
    output_path = Path(__file__).parent / "INSTAGRAM_DATA_ANALYSIS.md"
    
    print("=" * 60)
    print("Instagram Excel Data Analyzer")
    print("=" * 60)
    
    # Find Excel files
    excel_files = list(files_dir.glob("*.xlsx")) + list(files_dir.glob("*.xls"))
    print(f"\nFound {len(excel_files)} Excel file(s):\n")
    
    for f in excel_files:
        print(f"  - {f.name}")
    
    # Analyze each file
    print("\n" + "-" * 60)
    print("Analyzing files...")
    print("-" * 60)
    
    analyses = []
    for filepath in excel_files:
        print(f"\nProcessing: {filepath.name}")
        analysis = analyze_excel_file(str(filepath))
        analyses.append(analysis)
        print(f"  ✓ Found {len(analysis['unique_instagram_links'])} unique Instagram links")
    
    # Find cross-file duplicates
    print("\n" + "-" * 60)
    print("Checking for cross-file duplicates...")
    print("-" * 60)
    
    cross_duplicates = find_duplicates_across_files(analyses)
    print(f"  ✓ Found {len(cross_duplicates)} links appearing in multiple files")
    
    # Generate report
    print("\n" + "-" * 60)
    print("Generating report...")
    print("-" * 60)
    
    generate_report(analyses, cross_duplicates, str(output_path))
    print(f"  ✓ Report saved to: {output_path}")
    
    # Print summary
    all_unique = set()
    for a in analyses:
        all_unique.update(a['unique_instagram_links'])
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total files analyzed: {len(analyses)}")
    print(f"  Total unique Instagram pages: {len(all_unique)}")
    print(f"  Cross-file duplicates: {len(cross_duplicates)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
