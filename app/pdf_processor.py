"""PDF Parsing and Link Extraction Module"""
import re
import pdfplumber
from typing import List, Set
from pathlib import Path

class PDFProcessor:
    """Extracts and deduplicates links from PDF files"""
    
    # Enhanced URL pattern to catch more link formats
    LINK_REGEX = r'(https?://[^\s]+|www\.[^\s]+|(?:linkedin|github)\.com/[^\s]+)'
    URL_PATTERN = re.compile(LINK_REGEX, re.IGNORECASE)
    
    # Keywords to exclude (not real URLs)
    EXCLUDE_KEYWORDS = [
        'link', 'url', 'website', 'http', 'https', 'www',
        'example.com', 'yoursite.com', 'website.com'
    ]
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding https:// if missing
        
        Args:
            url: Raw URL string
            
        Returns:
            Normalized URL with proper scheme
        """
        url = url.strip()
        
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?)')
        
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and not a keyword/placeholder
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid URL, False otherwise
        """
        url_lower = url.lower()
        
        # Exclude common keywords
        for keyword in self.EXCLUDE_KEYWORDS:
            if url_lower == keyword or url_lower == f"https://{keyword}" or url_lower == f"http://{keyword}":
                return False
        
        # Must have a domain extension
        if '.' not in url:
            return False
        
        # Exclude very short URLs (likely not real)
        if len(url) < 8:
            return False
        
        # Exclude URLs that are just the word "link" or similar
        url_without_scheme = url_lower.replace('https://', '').replace('http://', '').replace('www.', '')
        if url_without_scheme in self.EXCLUDE_KEYWORDS:
            return False
        
        return True
    
    def extract_links_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract all URLs from a single PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of normalized and validated URLs
        """
        links = set()
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract from text content
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        found_links = self.URL_PATTERN.findall(text)
                        for link in found_links:
                            normalized = self.normalize_url(link)
                            if self.is_valid_url(normalized):
                                links.add(normalized)
                    
                    # Extract hyperlinks from annotations
                    if page.annots:
                        for annot in page.annots:
                            if 'uri' in annot:
                                uri = annot['uri']
                                normalized = self.normalize_url(uri)
                                if self.is_valid_url(normalized):
                                    links.add(normalized)
        
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return []
        
        return sorted(list(links))  # Sort for consistency
    
    def process_folder(self, folder_path: str) -> dict:
        """
        Process all PDFs in a folder
        
        Args:
            folder_path: Path to folder containing PDFs
            
        Returns:
            Dictionary mapping filename to list of links
        """
        folder = Path(folder_path)
        results = {}
        
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {folder_path}")
            return results
        
        print(f"Found {len(pdf_files)} PDF file(s)")
        
        for pdf_file in pdf_files:
            print(f"  Processing: {pdf_file.name}...")
            links = self.extract_links_from_pdf(str(pdf_file))
            if links:
                results[pdf_file.name] = links
                print(f"    ✓ Extracted {len(links)} links")
            else:
                print(f"    ⚠ No links found")
        
        return results
    
    def deduplicate_links(self, all_links: List[str]) -> List[str]:
        """
        Remove duplicate links
        
        Args:
            all_links: List of URLs (may contain duplicates)
            
        Returns:
            List of unique URLs
        """
        return sorted(list(set(all_links)))
    
    def get_all_unique_links(self, folder_results: dict) -> List[str]:
        """
        Get all unique links from folder processing results
        
        Args:
            folder_results: Dictionary from process_folder()
            
        Returns:
            List of all unique links across all PDFs
        """
        all_links = []
        for links in folder_results.values():
            all_links.extend(links)
        return self.deduplicate_links(all_links)