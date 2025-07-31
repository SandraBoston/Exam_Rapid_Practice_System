#!/usr/bin/env python3
"""
HTML to JSON Extractor for PCEP Exam Data
==========================================

This module extracts JSON objects from JavaScript "let data = {...}" statements
in HTML exam files and saves them as clean JSON files.

Purpose:
- Process all HTML files in Exam_HTML_Raw_Data folder
- Extract embedded JavaScript data objects
- Save as clean JSON files in Exam_HTML_Raw_Data_JSON_ONLY folder
- Preserve original filenames with .json extension

Features:
- Robust regex pattern matching for various JavaScript formats
- Handles "let data = {...}", "var data = {...}", "const data = {...}"
- JSON validation and formatting
- Error handling and progress reporting
- Creates output directory if it doesn't exist

Usage:
    python html_to_json_extractor.py

Author: PCEP Rapid Practice System
Date: 2025-07-30
Version: 1.0
"""

import json
import re
import os
from pathlib import Path
import sys

class HTMLToJSONExtractor:
    """Extract JSON data from HTML files containing JavaScript data objects."""
    
    def __init__(self, input_dir="Exam_HTML_Raw_Data", output_dir="Exam_HTML_Raw_Data_JSON_ONLY"):
        """
        Initialize the extractor.
        
        Args:
            input_dir (str): Directory containing HTML files
            output_dir (str): Directory to save extracted JSON files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processed_count = 0
        self.error_count = 0
        self.extracted_count = 0
        
    def setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Output directory ready: {self.output_dir}")
            return True
        except Exception as e:
            print(f"❌ Error creating output directory: {e}")
            return False
    
    def extract_json_from_html(self, html_content):
        """
        Extract JSON data from HTML content using regex patterns.
        
        Args:
            html_content (str): HTML file content
            
        Returns:
            dict or None: Extracted JSON data or None if not found
        """
        # Pattern to match various JavaScript data declarations
        patterns = [
            r'let\s+data\s*=\s*({.*?});',          # let data = {...};
            r'var\s+data\s*=\s*({.*?});',          # var data = {...};
            r'const\s+data\s*=\s*({.*?});',        # const data = {...};
            r'let\s+data\s*=\s*({.*?})\s*;',       # let data = {...} ;
            r'var\s+data\s*=\s*({.*?})\s*;',       # var data = {...} ;
            r'const\s+data\s*=\s*({.*?})\s*;',     # const data = {...} ;
        ]
        
        for pattern in patterns:
            # Use DOTALL flag to match across multiple lines
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if matches:
                json_str = matches[0]  # Get the first match
                
                try:
                    # Clean up the JSON string
                    json_str = json_str.strip()
                    
                    # Try to parse the JSON to validate it
                    json_data = json.loads(json_str)
                    
                    print(f"   ✅ Found valid JSON data using pattern: {pattern[:20]}...")
                    return json_data
                    
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Found JSON-like content but parsing failed: {str(e)[:50]}...")
                    continue
        
        return None
    
    def extract_json_from_file(self, html_file_path):
        """
        Extract JSON from a single HTML file.
        
        Args:
            html_file_path (Path): Path to HTML file
            
        Returns:
            dict or None: Extracted JSON data or None if extraction failed
        """
        try:
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Extract JSON data
            json_data = self.extract_json_from_html(html_content)
            
            if json_data:
                return json_data
            else:
                print(f"   ❌ No JSON data found in {html_file_path.name}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error reading {html_file_path.name}: {e}")
            return None
    
    def save_json_file(self, json_data, output_file_path):
        """
        Save JSON data to file with proper formatting.
        
        Args:
            json_data (dict): JSON data to save
            output_file_path (Path): Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Saved JSON to: {output_file_path.name}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving JSON file: {e}")
            return False
    
    def get_output_filename(self, html_filename):
        """
        Generate output JSON filename from HTML filename.
        
        Args:
            html_filename (str): Original HTML filename
            
        Returns:
            str: JSON filename
        """
        # Replace .html extension with .json
        return html_filename.replace('.html', '.json').replace('.HTML', '.json')
    
    def process_single_file(self, html_file_path):
        """
        Process a single HTML file and extract JSON.
        
        Args:
            html_file_path (Path): Path to HTML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"📄 Processing: {html_file_path.name}")
        
        # Extract JSON data
        json_data = self.extract_json_from_file(html_file_path)
        
        if json_data:
            # Generate output filename
            output_filename = self.get_output_filename(html_file_path.name)
            output_file_path = self.output_dir / output_filename
            
            # Save JSON file
            if self.save_json_file(json_data, output_file_path):
                self.extracted_count += 1
                return True
            else:
                self.error_count += 1
                return False
        else:
            self.error_count += 1
            return False
    
    def process_all_files(self):
        """Process all HTML files in the input directory."""
        print("🚀 HTML TO JSON EXTRACTOR")
        print("=" * 50)
        
        # Setup output directory
        if not self.setup_output_directory():
            return False
        
        # Check if input directory exists
        if not self.input_dir.exists():
            print(f"❌ Input directory not found: {self.input_dir}")
            return False
        
        # Find all HTML files
        html_files = list(self.input_dir.glob("*.html")) + list(self.input_dir.glob("*.HTML"))
        
        if not html_files:
            print(f"❌ No HTML files found in {self.input_dir}")
            return False
        
        print(f"📁 Found {len(html_files)} HTML files in {self.input_dir}")
        print("=" * 50)
        
        # Process each file
        for i, html_file in enumerate(html_files, 1):
            print(f"\n[{i}/{len(html_files)}]", end=" ")
            self.process_single_file(html_file)
            self.processed_count += 1
        
        # Print summary
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print processing summary."""
        print("\n" + "=" * 50)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 50)
        print(f"📁 Files processed: {self.processed_count}")
        print(f"✅ JSON files extracted: {self.extracted_count}")
        print(f"❌ Files with errors: {self.error_count}")
        print(f"📂 Output directory: {self.output_dir}")
        
        if self.extracted_count > 0:
            print(f"\n🎉 Successfully extracted JSON from {self.extracted_count} files!")
            print(f"💡 Check the '{self.output_dir}' folder for extracted JSON files.")
        else:
            print("\n⚠️  No JSON data was successfully extracted.")
            print("💡 Check if HTML files contain 'let data = {...}' JavaScript statements.")

def main():
    """Main function to run the extractor."""
    try:
        extractor = HTMLToJSONExtractor()
        extractor.process_all_files()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Extraction interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
