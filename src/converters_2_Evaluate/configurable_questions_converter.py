#!/usr/bin/env python3
"""
Configurable Questions Converter for PCEP Exam Practice App
===========================================================

This script converts quiz data to Python format with configurable input and output files.

Usage:
    python configurable_questions_converter.py [input_file] [output_file]
    
Examples:
    # Use default files
    python configurable_questions_converter.py
    
    # Specify output file only
    python configurable_questions_converter.py my_questions.py
    
    # Specify both input and output files
    python configurable_questions_converter.py input.html output.py

Arguments:
    input_file   : Path to HTML file containing quiz data (optional, uses embedded data if not provided)
    output_file  : Path for the generated Python questions file (default: pcep_module_4_questions.py)

Dependencies:
    pip install pygments

Author: PCEP Rapid Practice App Development Team
Version: 2.0
Date: 2025-06-27
"""

import json
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import html

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install dependencies with: pip install pygments")
    exit(1)

# The embedded quiz data from the PE1 Module 4 Test HTML file
EMBEDDED_QUIZ_DATA = {
    "questions": [
        {
            "id": 65658,
            "question": "<p>The following snippet:</p>\n\n<code class=\"codep\">def func_1(a):\n    return a ** a\n\n\ndef func_2(a):\n    return func_1(a) * func_1(a)\n\n\nprint(func_2(2))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247562, "option": "<p>will output <code >16</code></p>"},
                {"id": 247563, "option": "<p>will output <code >4</code></p>"},
                {"id": 247564, "option": "<p>will output <code >2</code></p>"},
                {"id": 247565, "option": "<p>is erroneous</p>"}
            ]
        },
        {
            "id": 65667,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def fun(inp=2, out=3):\n    return inp * out\n\n\nprint(fun(out=2))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247598, "option": "<p><code >4</code></p>"},
                {"id": 247599, "option": "<p><code >6</code></p>"},
                {"id": 247600, "option": "<p><code >2</code></p>"},
                {"id": 247601, "option": "<p>the snippet is erroneous</p>"}
            ]
        },
        {
            "id": 65663,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def any():\n    print(var + 1, end='')\n\n\nvar = 1\nany()\nprint(var)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247582, "option": "<p><code >21</code></p>"},
                {"id": 247583, "option": "<p><code >12</code></p>"},
                {"id": 247584, "option": "<p><code >11</code></p>"},
                {"id": 247585, "option": "<p><code >22</code></p>"}
            ]
        },
        {
            "id": 65671,
            "question": "<p>What is the output of the following code?</p>\n\n<p><code class=\"codep\">try:\n    value = input(\"Enter a value: \")\n    print(value/value)\nexcept ValueError:\n    print(\"Bad input...\")\nexcept ZeroDivisionError:\n    print(\"Very bad input...\")\nexcept TypeError:\n    print(\"Very very bad input...\")\nexcept:\n    print(\"Booo!\")\n\n</code></p>",
            "type": "Single Choice",
            "options": [
                {"id": 247614, "option": "<p><code >Very very bad input...</code></p>"},
                {"id": 247615, "option": "<p><code >Very bad input...</code></p>"},
                {"id": 247616, "option": "<p><code >Bad input...</code></p>"},
                {"id": 247617, "option": "<p><code >Booo!</code></p>"}
            ]
        },
        {
            "id": 65657,
            "question": "<p>The following snippet:</p>\n\n<code class=\"codep\">def func(a, b):\n    return a ** a\n\n\nprint(func(2))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247558, "option": "<p>is erroneous</p>"},
                {"id": 247559, "option": "<p>will output <code >4</code></p>"},
                {"id": 247560, "option": "<p>will output <code >2</code></p>"},
                {"id": 247561, "option": "<p>will return <code >None</code></p>"}
            ]
        },
        {
            "id": 65668,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">dictionary = {'one': 'two', 'three': 'one', 'two': 'three'}\nv = dictionary['one']\n\nfor k in range(len(dictionary)):\n    v = dictionary[v]\n\nprint(v)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247602, "option": "<p><code >two</code></p>"},
                {"id": 247603, "option": "<p><code >three</code></p>"},
                {"id": 247604, "option": "<p><code >one</code></p>"},
                {"id": 247605, "option": "<p><code >('one', 'two', 'three')</code></p>"}
            ]
        },
        {
            "id": 65650,
            "question": "<p>Which one of the following lines properly starts a parameterless function definition?</p>",
            "type": "Single Choice",
            "options": [
                {"id": 247530, "option": "<p><code >def fun():</code></p>"},
                {"id": 247531, "option": "<p><code >def fun:</code></p>"},
                {"id": 247532, "option": "<p><code >function fun():</code></p>"},
                {"id": 247533, "option": "<p><code >fun function():</code></p>"}
            ]
        },
        {
            "id": 65652,
            "question": "<p>A built-in function is a function which:</p>",
            "type": "Single Choice",
            "options": [
                {"id": 247538, "option": "<p>comes with Python, and is an integral part of Python</p>"},
                {"id": 247539, "option": "<p>has been placed within your code by another programmer</p>"},
                {"id": 247540, "option": "<p>has to be imported before use</p>"},
                {"id": 247541, "option": "<p>is hidden from programmers</p>"}
            ]
        },
        {
            "id": 65662,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def fun(x):\n    global y\n    y = x * x\n    return y\n\n\nfun(2)\nprint(y)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247578, "option": "<p><code >4</code></p>"},
                {"id": 247579, "option": "<p><code >2</code></p>"},
                {"id": 247580, "option": "<p>None</p>"},
                {"id": 247581, "option": "<p>the code will cause a runtime error</p>"}
            ]
        },
        {
            "id": 65670,
            "question": "<p>Select the <u>true</u> statements about the <i>try-except</i> block in relation to the following example. (Select <u>two</u> answers.)</p>\n\n<p><code class=\"codep\">try:\n    # Some code is here...\nexcept:\n    # Some code is here...\n\n</code></p>",
            "type": "Multiple Choice",
            "options": [
                {"id": 247610, "option": "<p>If you suspect that a snippet may raise an exception, you should place it in the <code >try</code> block.</p>"},
                {"id": 247611, "option": "<p>The code that follows the <code >except</code> statement will be executed if the code in the <code >try</code> clause runs into an error.</p>"},
                {"id": 247612, "option": "<p>If there is a syntax error in code located in the <code >try</code> block, the <code >except</code> branch will <b>not</b> handle it, and a <i>SyntaxError</i> exception will be raised instead.</p>"},
                {"id": 247613, "option": "<p>The code that follows the <code >try</code> statement will be executed if the code in the <code >except</code> clause runs into an error.</p>"}
            ]
        },
        {
            "id": 65655,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def fun(x):\n    x += 1\n    return x\n\n\nx = 2\nx = fun(x + 1)\nprint(x)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247550, "option": "<p><code >4</code></p>"},
                {"id": 247551, "option": "<p><code >5</code></p>"},
                {"id": 247552, "option": "<p><code >3</code></p>"},
                {"id": 247553, "option": "<p>the code is erroneous</p>"}
            ]
        },
        {
            "id": 65656,
            "question": "<p>What code would you insert instead of the comment to obtain the expected output?</p>\n\n<p>Expected output:</p>\n<code class=\"codep\">a\nb\nc</code>\n<br>\n\n<p>Code:</p>\n\n<code class=\"codep\">dictionary = {}\nmy_list = ['a', 'b', 'c', 'd']\n\nfor i in range(len(my_list) - 1):\n    dictionary[my_list[i]] = (my_list[i], )\n\nfor i in sorted(dictionary.keys()):\n    k = dictionary[i]\n    <mark style=\"background-color:#e6f2ff;\"># Insert your code here.</mark>\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247554, "option": "<p><code >print(k[0])</code></p>"},
                {"id": 247555, "option": "<p><code >print(k['0'])</code></p>"},
                {"id": 247556, "option": "<p><code >print(k)</code></p>"},
                {"id": 247557, "option": "<p><code >print(k[\"0\"])</code></p>"}
            ]
        },
        {
            "id": 65653,
            "question": "<p>The fact that tuples belong to sequence types means that:</p>",
            "type": "Single Choice",
            "options": [
                {"id": 247542, "option": "<p>they can be indexed and sliced like lists</p>"},
                {"id": 247543, "option": "<p>they can be extended using the <code >.append()</code> method</p>"},
                {"id": 247544, "option": "<p>they can be modified using the <code >del</code> instruction</p>"},
                {"id": 247545, "option": "<p>they are actually lists</p>"}
            ]
        },
        {
            "id": 65651,
            "question": "<p>A function defined in the following way:  (Select <u>two</u> answers)</p>\n\n<code class=\"codep\">def function(x=0):\n    return x\n\n</code>\n<br>",
            "type": "Multiple Choice",
            "options": [
                {"id": 247534, "option": "<p>may be invoked without any argument</p>"},
                {"id": 247535, "option": "<p>must be invoked with exactly one argument</p>"},
                {"id": 247536, "option": "<p>may be invoked with exactly one argument</p>"},
                {"id": 247537, "option": "<p>must be invoked without any argument</p>"}
            ]
        },
        {
            "id": 65666,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def fun(x, y, z):\n    return x + 2 * y + 3 * z\n\n\nprint(fun(0, z=1, y=3))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247594, "option": "<p><code >9</code></p>"},
                {"id": 247595, "option": "<p><code >0</code></p>"},
                {"id": 247596, "option": "<p><code >3</code></p>"},
                {"id": 247597, "option": "<p>the snippet is erroneous</p>"}
            ]
        },
        {
            "id": 65669,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">tup = (1, 2, 4, 8)\ntup = tup[1:-1]\ntup = tup[0]\nprint(tup)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247606, "option": "<p><code >2</code></p>"},
                {"id": 247607, "option": "<p><code >(2)</code></p>"},
                {"id": 247608, "option": "<p><code >(2, )</code></p>"},
                {"id": 247609, "option": "<p>the snippet is erroneous</p>"}
            ]
        },
        {
            "id": 65654,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def f(x):\n    if x == 0:\n    \treturn 0\n    return x + f(x - 1)\n    \n\t\nprint(f(3))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247546, "option": "<p><code >6</code></p>"},
                {"id": 247547, "option": "<p><code >3</code></p>"},
                {"id": 247548, "option": "<p><code >1</code></p>"},
                {"id": 247549, "option": "<p>the code is erroneous</p>"}
            ]
        },
        {
            "id": 65661,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">def fun(x):\n    if x % 2 == 0:\n    \treturn 1\n    else:\n    \treturn\n\n\nprint(fun(fun(2)) + 1)\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247574, "option": "<p>the code will cause a runtime error</p>"},
                {"id": 247575, "option": "<p><code >1</code></p>"},
                {"id": 247576, "option": "<p><code >2</code></p>"},
                {"id": 247577, "option": "<p><code >None</code></p>"}
            ]
        },
        {
            "id": 65664,
            "question": "<p>Assuming that <code >my_tuple</code> is a correctly created tuple, the fact that tuples are immutable means that the following instruction:</p>\n\n<code class=\"codep\">my_tuple[1] = my_tuple[1] + my_tuple[0]\n\n</code>\n<br>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247586, "option": "<p>is illegal</p>"},
                {"id": 247587, "option": "<p>can be executed if and only if the tuple contains at least two elements</p>"},
                {"id": 247588, "option": "<p>is fully correct</p>"},
                {"id": 247589, "option": "<p>may be illegal if the tuple contains strings</p>"}
            ]
        },
        {
            "id": 65665,
            "question": "<p>What is the output of the following snippet?</p>\n\n<code class=\"codep\">my_list =  ['Mary', 'had', 'a', 'little', 'lamb']\n\n\ndef my_list(my_list):\n    del my_list[3]\n    my_list[3] = 'ram'\n\n\nprint(my_list(my_list))\n\n</code>\n<br>",
            "type": "Single Choice",
            "options": [
                {"id": 247590, "option": "<p>no output, the snippet is erroneous</p>"},
                {"id": 247591, "option": "<p><code >['Mary', 'had', 'a', 'little', 'lamb']</code></p>"},
                {"id": 247592, "option": "<p><code >['Mary', 'had', 'a', 'lamb']</code></p>"},
                {"id": 247593, "option": "<p><code >['Mary', 'had', 'a', 'ram']</code></p>"}
            ]
        },
        {
            "id": 65660,
            "question": "<p>Which of the following statements are <u>true</u>?   (Select <u>two</u> answers)</p>",
            "type": "Multiple Choice",
            "options": [
                {"id": 247570, "option": "<p>The <code >None</code> value cannot be used outside functions</p>"},
                {"id": 247571, "option": "<p>The <code >None</code> value can be assigned to variables</p>"},
                {"id": 247572, "option": "<p>The <code >None</code> value can be compared with variables</p>"},
                {"id": 247573, "option": "<p>The <code >None</code> value can be used as an argument of arithmetic operators</p>"}
            ]
        },
        {
            "id": 65659,
            "question": "<p>Which of the following lines properly starts a function using two parameters, both with zeroed default values?</p>",
            "type": "Single Choice",
            "options": [
                {"id": 247566, "option": "<p><code >def fun(a=0, b=0):</code></p>"},
                {"id": 247567, "option": "<p><code >def fun(a=b=0):</code></p>"},
                {"id": 247568, "option": "<p><code >fun fun(a=0, b):</code></p>"},
                {"id": 247569, "option": "<p><code >fun fun(a, b=0):</code></p>"}
            ]
        }
    ]
}


class ConfigurableQuestionConverter:
    """Converts quiz data to structured question format with syntax highlighting."""
    
    def __init__(self):
        self.python_lexer = PythonLexer()
        self.html_formatter = HtmlFormatter(
            style='default',
            cssclass='highlight',
            linenos=False,
            noclasses=False
        )
        
    def clean_html_text(self, html_text: str) -> str:
        """Clean HTML text and return plain text."""
        if not html_text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        # Decode HTML entities
        text = html.unescape(text)
        return text.strip()

    def extract_code_blocks(self, html_text: str) -> tuple:
        """Extract Python code blocks from HTML."""
        if not html_text:
            return "", []
        
        code_blocks = []
        # Look for code blocks
        code_pattern = r'<code[^>]*>(.*?)</code>'
        matches = re.findall(code_pattern, html_text, re.DOTALL)
        
        for code in matches:
            clean_code = html.unescape(code).strip()
            if clean_code and len(clean_code) > 5:  # Only process substantial code blocks
                # Apply syntax highlighting
                highlighted = highlight(clean_code, self.python_lexer, self.html_formatter)
                code_blocks.append({
                    'original': clean_code,
                    'highlighted': highlighted
                })
        
        # Clean the original text for display
        clean_text = re.sub(r'<code[^>]*>.*?</code>', '[CODE]', html_text, flags=re.DOTALL)
        clean_text = self.clean_html_text(clean_text)
        
        return clean_text, code_blocks

    def convert_questions(self, quiz_data: dict) -> List[Dict[str, Any]]:
        """Convert the quiz data to our format."""
        converted_questions = []
        
        for i, q in enumerate(quiz_data["questions"], 1):
            print(f"Processing question {i}/{len(quiz_data['questions'])}...")
            
            # Process question text
            question_text, question_code_blocks = self.extract_code_blocks(q["question"])
            
            # Process options
            options = []
            for opt in q["options"]:
                option_text, option_code_blocks = self.extract_code_blocks(opt["option"])
                options.append({
                    'id': opt["id"],
                    'text': option_text,
                    'code_blocks': option_code_blocks
                })
            
            # Convert to our format
            converted_question = {
                'id': q["id"],
                'question': question_text,
                'code_blocks': question_code_blocks,
                'options': options,
                'type': 'multiple' if q["type"] == 'Multiple Choice' else 'single',
                'multiple_choice': q["type"] == 'Multiple Choice',
                'explanation': f"This question is from PE1 Module 4 Test, covering Python functions, tuples, dictionaries, and exceptions."
            }
            
            converted_questions.append(converted_question)
        
        return converted_questions

    def load_quiz_data_from_html(self, html_file: str) -> Optional[Dict]:
        """Load quiz data from HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract JavaScript data from HTML
            pattern = r'let data = ({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                print(f"Could not find JavaScript data object in {html_file}")
                return None
                
            data_str = match.group(1)
            return json.loads(data_str)
            
        except FileNotFoundError:
            print(f"HTML file not found: {html_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JavaScript data from HTML: {e}")
            return None
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return None

    def generate_questions_file(self, output_file: str, quiz_data: dict) -> List[Dict[str, Any]]:
        """Generate the Python questions file."""
        print("Converting questions...")
        questions = self.convert_questions(quiz_data)
        
        # Generate CSS for syntax highlighting
        css = self.html_formatter.get_style_defs('.highlight')
        
        # Generate the Python file content
        content = f'''"""
PCEP Module 4 Test Questions Dataset
===================================

Auto-generated from PE1 -- Module 4 Test HTML file.
Contains all {len(questions)} questions with Python syntax highlighting and clean formatting.

Generated by: configurable_questions_converter.py
Date: 2025-06-27
Total Questions: {len(questions)}
"""

# Pygments CSS for syntax highlighting
PYGMENTS_CSS = """
{css}
"""

# Complete questions dataset
PCEP_MODULE_4_QUESTIONS = {json.dumps(questions, indent=2, ensure_ascii=False)}

# Helper functions
def get_all_questions():
    """Return all questions in the dataset."""
    return PCEP_MODULE_4_QUESTIONS

def get_question_by_id(question_id):
    """Get a specific question by ID."""
    for question in PCEP_MODULE_4_QUESTIONS:
        if question['id'] == question_id:
            return question
    return None

def get_question_count():
    """Get the total number of questions."""
    return len(PCEP_MODULE_4_QUESTIONS)

def get_single_choice_questions():
    """Get all single choice questions."""
    return [q for q in PCEP_MODULE_4_QUESTIONS if not q['multiple_choice']]

def get_multiple_choice_questions():
    """Get all multiple choice questions."""
    return [q for q in PCEP_MODULE_4_QUESTIONS if q['multiple_choice']]

if __name__ == "__main__":
    print(f"PCEP Module 4 Questions Dataset loaded successfully!")
    print(f"Total questions: {{get_question_count()}}")
    print(f"Single choice: {{len(get_single_choice_questions())}}")
    print(f"Multiple choice: {{len(get_multiple_choice_questions())}}")
    print(f"Question IDs: {{[q['id'] for q in PCEP_MODULE_4_QUESTIONS]}}")
'''
        
        # Save the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Questions file generated: {output_file}")
        print(f"📊 Total questions: {len(questions)}")
        print(f"📋 Single choice: {len([q for q in questions if not q['multiple_choice']])}")
        print(f"📋 Multiple choice: {len([q for q in questions if q['multiple_choice']])}")
        
        return questions


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("    python configurable_questions_converter.py [input_file] [output_file]")
    print("")
    print("Examples:")
    print("    # Use embedded data, default output file")
    print("    python configurable_questions_converter.py")
    print("")
    print("    # Use embedded data, custom output file")
    print("    python configurable_questions_converter.py my_questions.py")
    print("")
    print("    # Use custom HTML input and output files")
    print("    python configurable_questions_converter.py input.html output.py")
    print("")
    print("Arguments:")
    print("    input_file   : Path to HTML file containing quiz data (optional)")
    print("    output_file  : Path for generated Python questions file (default: pcep_module_4_questions.py)")


def main():
    """Main function to handle command line arguments and run conversion."""
    input_file = None
    output_file = "pcep_module_4_questions.py"
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # No arguments - use embedded data and default output
        pass
    elif len(sys.argv) == 2:
        # One argument - could be output file or input file
        arg = sys.argv[1]
        if arg in ['-h', '--help', 'help']:
            print_usage()
            return
        elif arg.endswith('.html'):
            input_file = arg
        else:
            output_file = arg
    elif len(sys.argv) == 3:
        # Two arguments - input and output files
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Error: Too many arguments")
        print_usage()
        return

    # Create converter
    converter = ConfigurableQuestionConverter()
    
    # Load quiz data
    if input_file:
        print(f"Loading quiz data from HTML file: {input_file}")
        quiz_data = converter.load_quiz_data_from_html(input_file)
        if not quiz_data:
            print("Failed to load quiz data from HTML file")
            return
    else:
        print("Using embedded quiz data")
        quiz_data = EMBEDDED_QUIZ_DATA
    
    print(f"Output file: {output_file}")
    print("=" * 50)
    
    # Convert and generate
    questions = converter.generate_questions_file(output_file, quiz_data)
    print("\n✅ Conversion completed successfully!")


if __name__ == "__main__":
    main()
