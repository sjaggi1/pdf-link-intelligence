#!/usr/bin/env python3
"""
Smart PDF Link Intelligence & Automation Platform
Main application entry point
"""
import argparse
import sys
from pathlib import Path

from app.pdf_processor import PDFProcessor
from app.link_classifier import LinkClassifier
from app.link_validator import LinkValidator
from app.browser_manager import BrowserManager
from app.report_generator import ReportGenerator

print("🔥 main.py EXECUTED 🔥")


class PDFLinkIntelligence:
    """Main application orchestrator"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.classifier = LinkClassifier()
        self.validator = LinkValidator()
        self.reporter = ReportGenerator()
    
    def process_single_pdf(self, pdf_path: str, args):
        """Process a single PDF file"""
        print(f"\n📄 Processing: {pdf_path}")
        
        # Extract links
        links = self.pdf_processor.extract_links_from_pdf(pdf_path)
        if not links:
            print("❌ No links found in PDF")
            return
        
        print(f"✓ Extracted {len(links)} links")
        
        # Classify links
        categorized = self.classifier.classify_batch(links)
        
        # Validate if requested
        validation_results = None
        if args.validate:
            print(f"\n🔍 Validating {len(links)} links...")
            validation_results = self.validator.validate_batch(links)
            alive_links = self.validator.filter_alive(validation_results)
            print(f"✓ {len(alive_links)} alive, {len(links)-len(alive_links)} dead")
            
            # Use only alive links
            if args.skip_dead:
                links = alive_links
                categorized = self.classifier.classify_batch(links)
        
        # Generate reports
        if args.report:
            csv_path = self.reporter.generate_csv_report(links, categorized, validation_results)
            json_path = self.reporter.generate_json_summary(len(links), categorized, validation_results)
            print(f"\n📊 Reports generated:")
            print(f"  CSV : {csv_path}")
            print(f"  JSON: {json_path}")
        
        # Print summary
        self.reporter.print_summary(categorized, validation_results)
        
        # Open links
        if args.dry_run:
            browser = BrowserManager(batch_size=args.batch_size)
            browser.dry_run(links)
        elif not args.no_open:
            self._open_links(links, categorized, args)
    
    def process_folder(self, folder_path: str, args):
        """Process multiple PDFs from a folder"""
        print(f"\n📁 Processing folder: {folder_path}")
        
        folder_results = self.pdf_processor.process_folder(folder_path)
        
        if not folder_results:
            print("❌ No PDFs found or no links extracted")
            return
        
        print(f"✓ Processed {len(folder_results)} PDF files")
        
        # Get all unique links
        all_links = self.pdf_processor.get_all_unique_links(folder_results)
        print(f"✓ Found {len(all_links)} unique links")
        
        # Continue with same logic as single PDF
        categorized = self.classifier.classify_batch(all_links)
        
        validation_results = None
        if args.validate:
            print(f"\n🔍 Validating {len(all_links)} links...")
            validation_results = self.validator.validate_batch(all_links)
            alive_links = self.validator.filter_alive(validation_results)
            print(f"✓ {len(alive_links)} alive, {len(all_links)-len(alive_links)} dead")
            
            if args.skip_dead:
                all_links = alive_links
                categorized = self.classifier.classify_batch(all_links)
        
        if args.report:
            csv_path = self.reporter.generate_csv_report(all_links, categorized, validation_results)
            json_path = self.reporter.generate_json_summary(len(all_links), categorized, validation_results)
            print(f"\n📊 Reports generated:")
            print(f"  CSV : {csv_path}")
            print(f"  JSON: {json_path}")
        
        self.reporter.print_summary(categorized, validation_results)
        
        if args.dry_run:
            browser = BrowserManager(batch_size=args.batch_size)
            browser.dry_run(all_links)
        elif not args.no_open:
            self._open_links(all_links, categorized, args)
    
    def _open_links(self, links, categorized, args):
        """Handle link opening with priority"""
        browser = BrowserManager(
            batch_size=args.batch_size,
            delay_minutes=args.delay
        )
        
        if args.resume_mode or args.priority:
            # Priority-based opening
            priority = args.priority.split(',') if args.priority else None
            sorted_categories = self.classifier.get_priority_sorted(categorized, priority)
            
            print(f"\n🚀 Opening links by priority...")
            for category, cat_links in sorted_categories:
                print(f"\n--- Opening {category.upper()} links ({len(cat_links)}) ---")
                browser.open_all_batches(cat_links, interactive=args.interactive)
        else:
            # Standard batch opening
            print(f"\n🚀 Opening all links...")
            browser.open_all_batches(links, interactive=args.interactive)

def main():
    parser = argparse.ArgumentParser(
        description='Smart PDF Link Intelligence & Automation Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input', help='PDF file or folder path')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Number of links per batch (default: 10)')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between batches in minutes (default: 0.5)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate link health before opening')
    parser.add_argument('--skip-dead', action='store_true',
                       help='Skip dead links (requires --validate)')
    parser.add_argument('--resume-mode', action='store_true',
                       help='Auto-prioritize for resume/CV links')
    parser.add_argument('--priority', type=str,
                       help='Custom priority order (e.g., github,portfolio,linkedin)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview links without opening')
    parser.add_argument('--no-open', action='store_true',
                       help='Extract and analyze only, do not open links')
    parser.add_argument('--report', action='store_true',
                       help='Generate CSV and JSON reports')
    parser.add_argument('--interactive', action='store_true',
                       help='Wait for user confirmation between batches')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"❌ Error: {args.input} does not exist")
        sys.exit(1)
    
    app = PDFLinkIntelligence()
    
    if input_path.is_file():
        app.process_single_pdf(str(input_path), args)
    elif input_path.is_dir():
        app.process_folder(str(input_path), args)
    else:
        print("❌ Error: Input must be a PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()