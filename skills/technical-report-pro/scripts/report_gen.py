#!/usr/bin/env python3
"""
Technical Report Generator
===========================
Generate professional technical reports from templates.

Usage:
    python report_gen.py --type arch-review --title "System Architecture"
    python report_gen.py --type post-mortem --title "Incident Analysis" --scan research/
    python report_gen.py --list  # List available templates
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

# Template directory relative to this script
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "assets" / "templates"
EXAMPLES_DIR = SCRIPT_DIR.parent / "references" / "examples"

TEMPLATE_TYPES = {
    "arch-review": "Architecture Review",
    "post-mortem": "Post-Mortem",
    "research-summary": "Research Summary",
    "debug-investigation": "Debug Investigation"
}


def list_templates():
    """List available templates."""
    print("Available report templates:\n")
    for key, name in TEMPLATE_TYPES.items():
        template_file = TEMPLATES_DIR / f"{key}.md"
        status = "✅" if template_file.exists() else "❌"
        print(f"  {status} {key:25} - {name}")
    print()


def load_template(template_type: str) -> str:
    """Load a template file."""
    template_file = TEMPLATES_DIR / f"{template_type}.md"
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")
    return template_file.read_text()


def scan_for_context(scan_path: str, keywords: list = None) -> str:
    """Scan a directory for relevant context."""
    path = Path(scan_path)
    if not path.exists():
        return f"(Scan path not found: {scan_path})"
    
    context_lines = []
    context_lines.append(f"## Context from {scan_path}\n")
    
    # List files
    files = list(path.rglob("*.md"))[:20]  # Limit to 20 files
    if files:
        context_lines.append("### Files found:")
        for f in files:
            context_lines.append(f"- {f.relative_to(path)}")
    
    # If keywords provided, search for them
    if keywords:
        context_lines.append("\n### Keyword matches:")
        for kw in keywords:
            for f in files:
                content = f.read_text()
                if kw.lower() in content.lower():
                    context_lines.append(f"- '{kw}' found in {f.name}")
    
    return "\n".join(context_lines)


def generate_report_id(report_type: str) -> str:
    """Generate a unique report ID."""
    prefix_map = {
        "arch-review": "ARCH",
        "post-mortem": "PM",
        "research-summary": "RS",
        "debug-investigation": "DBG"
    }
    prefix = prefix_map.get(report_type, "RPT")
    date = datetime.now().strftime("%Y%m%d")
    seq = datetime.now().strftime("%H%M")
    return f"{prefix}-{date}-{seq}"


def fill_basic_placeholders(template: str, title: str, author: str = "Archie") -> str:
    """Fill in basic placeholders with actual values."""
    date = datetime.now().strftime("%Y-%m-%d")
    
    replacements = {
        "{{TITLE}}": title,
        "{{DATE}}": date,
        "{{AUTHOR}}": author,
        "{{STATUS}}": "Draft",
        "{{SEQ}}": datetime.now().strftime("%H%M"),
    }
    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    return template


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional technical reports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--type", "-t", choices=TEMPLATE_TYPES.keys(),
                        help="Report type to generate")
    parser.add_argument("--title", help="Report title")
    parser.add_argument("--author", default="Archie", help="Author name")
    parser.add_argument("--scan", help="Directory to scan for context")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    
    if args.list:
        list_templates()
        return
    
    if not args.type:
        parser.print_help()
        print("\nError: --type is required")
        return
    
    if not args.title:
        args.title = f"{TEMPLATE_TYPES[args.type]} Report"
    
    # Load and fill template
    template = load_template(args.type)
    report = fill_basic_placeholders(template, args.title, args.author)
    
    # Add context if scan requested
    if args.scan:
        context = scan_for_context(args.scan)
        report += f"\n\n---\n\n{context}"
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"✅ Report generated: {output_path}")
    else:
        # Generate default output path
        report_id = generate_report_id(args.type)
        output_file = f"{report_id}_{args.type}.md"
        Path(output_file).write_text(report)
        print(f"✅ Report generated: {output_file}")


if __name__ == "__main__":
    main()
