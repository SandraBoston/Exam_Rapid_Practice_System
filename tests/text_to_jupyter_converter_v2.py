#!/usr/bin/env python3
"""
Text to Jupyter Notebook Converter v2 

Converts text-based Python educational content into Jupyter Notebook format.
Specifically designed for PCEP exam materials and similar educational content.

Usage:
    python text_to_jupyter_converter_v2.py input_file.txt [output_file.ipynb]

If output_file is not provided, it will use the input filename with .ipynb extension.
"""

import re
import json
import argparse
import datetime
import os
import logging
from typing import List, Dict, Any, Tuple, Optional


def setup_logging() -> logging.Logger:
    """
    Set up logging configuration with datetime stamp in filename.
    
    Returns:
        Logger object configured for the application
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with datetime stamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"converter_log_{timestamp}.log")
    
    # Configure logger
    logger = logging.getLogger("text_to_jupyter")
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Log file: {log_filename}")
    return logger


def read_text_file(filepath: str, logger: logging.Logger) -> str:
    """
    Read content from a text file.
    
    Args:
        filepath: Path to the text file
        logger: Logger object for logging
        
    Returns:
        The content of the text file as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    logger.info(f"Reading file: {filepath}")
    
    # Try different paths if the file is not found
    possible_paths = [
        filepath,  # Try the original path first
        os.path.join(os.getcwd(), filepath),  # Try relative to current directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath),  # Try relative to script location
        os.path.join("Cisco_Practice_Exams", filepath),  # Try in Cisco_Practice_Exams subdirectory
        os.path.join("..", "Cisco_Practice_Exams", filepath)  # Try one level up in Cisco_Practice_Exams subdirectory
    ]
    
    for path in possible_paths:
        logger.debug(f"Trying path: {path}")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                logger.debug(f"Successfully read {len(content)} characters from file")
                return content
            except IOError as e:
                logger.error(f"Error reading file {path}: {str(e)}")
                raise
    
    # If we get here, the file wasn't found in any of the tried locations
    logger.error(f"File not found in any of the tried locations: {filepath}")
    raise FileNotFoundError(f"File not found: {filepath}")


def parse_content(content: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    """
    Parse text content into structured blocks for Jupyter notebook cells.
    
    Args:
        content: Text content to parse
        logger: Logger object for logging
        
    Returns:
        List of dictionaries representing Jupyter notebook cells
    """
    logger.info("Parsing content into notebook cells")
    cells = []
    
    # Split content into sections
    try:
        lines = content.split('\n')
        current_block = {"type": "markdown", "content": []}
        code_block = False
        
        for line in lines:
            # Detect section headers (like "4.6.2 Tuples")
            header_match = re.match(r'^(\d+\.\d+(?:\.\d+)?\s+.+)$', line)
            if header_match:
                # Save current block if not empty
                if current_block["content"]:
                    cells.append(create_cell(current_block))
                
                # Create header cell
                cells.append({
                    "cell_type": "markdown",
                    "source": [f"## {header_match.group(1)}"]
                })
                
                # Reset current block
                current_block = {"type": "markdown", "content": []}
                code_block = False
                continue
            
            # Detect code blocks
            if line.strip() == "```python" or line.lower().strip() == "output":
                # Save current block if not empty
                if current_block["content"]:
                    cells.append(create_cell(current_block))
                
                # Start a new code block
                current_block = {"type": "code", "content": []}
                code_block = True
                continue
                
            if line.strip() == "```" and code_block:
                # End of code block
                if current_block["content"]:
                    cells.append(create_cell(current_block))
                
                # Start a new markdown block
                current_block = {"type": "markdown", "content": []}
                code_block = False
                continue
            
            # Check for indented code blocks or standalone code snippets
            if not code_block and (re.match(r'^\s{4,}', line) or 
                                 re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', line) or
                                 re.match(r'^print\(', line) or
                                 re.match(r'^for\s+', line) or
                                 re.match(r'^if\s+', line) or
                                 re.match(r'^import\s+', line) or
                                 re.match(r'^def\s+', line)):
                
                # If previous content was markdown, save it
                if current_block["type"] == "markdown" and current_block["content"]:
                    cells.append(create_cell(current_block))
                    current_block = {"type": "code", "content": []}
                    
                # Set as code if not already
                if current_block["type"] != "code":
                    current_block = {"type": "code", "content": []}
                
                current_block["content"].append(line)
                continue
                
            # Regular line, add to current block
            current_block["content"].append(line)
        
        # Add the last block if not empty
        if current_block["content"]:
            cells.append(create_cell(current_block))
            
    except Exception as e:
        logger.error(f"Error parsing content: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to parse content: {str(e)}")
    
    logger.info(f"Parsed content into {len(cells)} cells")
    return cells


def create_cell(block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a Jupyter notebook cell from a parsed block.
    
    Args:
        block: Dictionary containing block type and content
        
    Returns:
        Dictionary representing a Jupyter notebook cell
    """
    if block["type"] == "code":
        return {
            "cell_type": "code",
            "source": block["content"],
            "execution_count": None,
            "outputs": []
        }
    else:  # markdown
        return {
            "cell_type": "markdown",
            "source": block["content"]
        }


def extract_code_blocks(text: str, logger: logging.Logger) -> List[Tuple[str, str]]:
    """
    Extract code blocks from text content.
    
    Args:
        text: Text content that may contain code blocks
        logger: Logger object for logging
        
    Returns:
        List of tuples containing (code, output)
    """
    logger.debug("Extracting code blocks from text")
    
    code_blocks = []
    try:
        # Pattern to match code blocks with possible output sections
        code_pattern = re.compile(r'```python\n(.*?)\n```\s*(?:Output\s*(.*?))?(?=```|\Z)', re.DOTALL)
        
        for match in code_pattern.finditer(text):
            code = match.group(1).strip()
            output = match.group(2).strip() if match.group(2) else ""
            code_blocks.append((code, output))
        
        # Also look for code-like patterns not in backticks
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if (re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', line) or 
                re.match(r'^print\(', line) or
                re.match(r'^for\s+', line) or
                re.match(r'^if\s+', line) or
                re.match(r'^import\s+', line) or
                re.match(r'^def\s+', line)):
                
                code_start = i
                while i < len(lines) and lines[i].strip():
                    i += 1
                code = '\n'.join(lines[code_start:i])
                code_blocks.append((code, ""))
            i += 1
    except Exception as e:
        logger.warning(f"Error extracting code blocks: {str(e)}")
    
    logger.debug(f"Extracted {len(code_blocks)} code blocks")
    return code_blocks


def process_quiz_section(content: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    """
    Process a quiz section, handling both text and code properly.
    
    Args:
        content: Quiz section content
        logger: Logger object for logging
        
    Returns:
        List of cell dictionaries for the quiz section
    """
    logger.info("Processing quiz section")
    
    cells = []
    try:
        # Add quiz title
        cells.append({
            "cell_type": "markdown",
            "source": ["## Quiz Section"]
        })
        
        # Split into individual questions
        # Fixed regex: using re.DOTALL flag instead of inline mode
        question_pattern = re.compile(r'Question\s+\d+[:.]?\s*(.*?)(?=Question\s+\d+|$)', re.DOTALL)
        questions = question_pattern.findall(content)
        
        for i, question in enumerate(questions, 1):
            question = question.strip()
            if not question:
                continue
                
            # Add question text as markdown
            cells.append({
                "cell_type": "markdown",
                "source": [f"### Question {i}", "", question.split('\n')[0]]
            })
            
            # Extract and add code if present
            code_match = re.search(r'```python\n(.*?)\n```', question, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                cells.append({
                    "cell_type": "code",
                    "source": code.split('\n'),
                    "execution_count": None,
                    "outputs": []
                })
            else:
                # Look for code patterns without markdown formatting
                code_lines = []
                in_code = False
                
                for line in question.split('\n'):
                    if (re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', line) or 
                        re.match(r'^print\(', line) or
                        re.match(r'^for\s+', line) or
                        re.match(r'^if\s+', line) or
                        re.match(r'^import\s+', line) or
                        re.match(r'^def\s+', line)):
                        
                        if not in_code:
                            in_code = True
                        
                        code_lines.append(line)
                    elif line.strip() and in_code and not line.startswith('Check'):
                        code_lines.append(line)
                    elif in_code and not line.strip():
                        # End of code block
                        in_code = False
                        
                        if code_lines:
                            cells.append({
                                "cell_type": "code",
                                "source": code_lines,
                                "execution_count": None,
                                "outputs": []
                            })
                            code_lines = []
                
                if code_lines:  # Add any remaining code
                    cells.append({
                        "cell_type": "code",
                        "source": code_lines,
                        "execution_count": None,
                        "outputs": []
                    })
            
            # Add options as markdown if it's a multiple choice question
            options_pattern = re.compile(r'(?:^|\n)([A-Da-d][).]\s+.*?)(?=\n[A-Da-d][).]|\Z)', re.DOTALL)
            options = options_pattern.findall(question)
            if options:
                cells.append({
                    "cell_type": "markdown",
                    "source": ["**Options:**", ""] + [f"- {opt.strip()}" for opt in options]
                })
    except Exception as e:
        logger.error(f"Error processing quiz section: {str(e)}")
        
    logger.info(f"Processed quiz section into {len(cells)} cells")
    return cells


def create_jupyter_notebook(cells: List[Dict[str, Any]], logger: logging.Logger) -> Dict[str, Any]:
    """
    Create a Jupyter notebook structure from parsed cells.
    
    Args:
        cells: List of cell dictionaries
        logger: Logger object for logging
        
    Returns:
        Jupyter notebook as a dictionary
    """
    logger.info("Creating Jupyter notebook structure")
    
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    logger.debug("Jupyter notebook structure created successfully")
    return notebook


def write_jupyter_notebook(notebook: Dict[str, Any], output_path: str, logger: logging.Logger) -> None:
    """
    Write Jupyter notebook to a file.
    
    Args:
        notebook: Jupyter notebook structure as a dictionary
        output_path: Path to write the notebook
        logger: Logger object for logging
        
    Raises:
        IOError: If there's an error writing the file
    """
    logger.info(f"Writing Jupyter notebook to {output_path}")
    
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(notebook, file, indent=2)
        logger.info(f"Successfully wrote Jupyter notebook to {output_path}")
    except IOError as e:
        logger.error(f"Error writing notebook to {output_path}: {str(e)}")
        raise


def main():
    """Main function to parse command line arguments and run the converter."""
    parser = argparse.ArgumentParser(
        description="Convert text files to Jupyter Notebook format."
    )
    parser.add_argument(
        "input_file", 
        help="Path to the input text file"
    )
    parser.add_argument(
        "output_file", 
        nargs="?", 
        help="Path to the output notebook file (optional)"
    )
    
    args = parser.parse_args()
    
    # Initialize logging
    logger = setup_logging()
    
    try:
        # Normalize input file path
        input_file = args.input_file
        
        # Determine output file path
        if args.output_file:
            output_path = args.output_file
        else:
            # Use input filename with .ipynb extension
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_dir = os.path.dirname(os.path.abspath(input_file)) if os.path.exists(input_file) else os.getcwd()
            output_path = os.path.join(output_dir, f"{base_name}.ipynb")
        
        logger.info(f"Converting {input_file} to {output_path}")
        
        # Read input file
        content = read_text_file(input_file, logger)
        
        # Check if content contains quiz section - FIXED: moved (?m) flag to beginning
        if re.search(r'SECTION QUIZ|^Question \d+:', content, re.MULTILINE):
            # Split into main content and quiz section - FIXED: Using re.MULTILINE flag
            parts = re.split(r'(SECTION QUIZ|^Question \d+:)', content, 1, re.MULTILINE)
            
            if len(parts) >= 3:
                main_content = parts[0]
                quiz_marker = parts[1]
                quiz_content = quiz_marker + parts[2]
                
                # Process main content
                cells = parse_content(main_content, logger)
                
                # Process quiz section
                quiz_cells = process_quiz_section(quiz_content, logger)
                cells.extend(quiz_cells)
            else:
                # Process everything as regular content
                cells = parse_content(content, logger)
        else:
            # Regular parsing for content without quiz section
            cells = parse_content(content, logger)
        
        # Create notebook structure
        notebook = create_jupyter_notebook(cells, logger)
        
        # Write notebook to file
        write_jupyter_notebook(notebook, output_path, logger)
        
        logger.info(f"Conversion completed successfully. Notebook saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
