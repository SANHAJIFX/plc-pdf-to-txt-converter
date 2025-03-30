# PLC Program PDF to Text Converter

A comprehensive tool to convert PLC program PDFs from TIA Portal to structured text format and split them into text files under 2MB for easier analysis and modification.

## 🌟 Overview

This project addresses the challenge of working with large, complex PLC program PDFs exported from TIA Portal. The solution converts these PDFs into structured text format while preserving program logic, comments, variable declarations, and hierarchical structure, and then splits them into manageable text files that don't exceed 2MB in size.

## 🚀 Features

- **Two-stage Conversion Process**:
  - Stage 1: Convert PLC program PDFs to structured text (.st) format
  - Stage 2: Convert structured text files to plain text (.txt) files under 2MB

- **Comprehensive Format Preservation**:
  - Maintains program logic, hierarchy, and execution sequences
  - Preserves variable names, data types, and memory addresses
  - Retains network structures and comments
  - Handles LAD/FBD diagram elements with text representations

- **Smart File Organization**:
  - Organizes files by PLC block types (OBs, FBs, FCs, DBs, etc.)
  - Splits large files into multiple parts with clear navigation markers
  - Adds metadata headers for traceability to original files

- **Specialized Processing**:
  - Handles various PLC block types with appropriate formatting
  - Processes specialized instructions (timers, counters, etc.)
  - Preserves tag tables and memory addresses

## 📂 Repository Structure

```
/
├── pdf_to_structured_text.py    # Main script for PDF to structured text conversion
├── convert_to_txt.py            # Script for structured text to TXT conversion with size limits
├── convert_pdfs.bat             # Windows batch file for PDF to ST conversion
├── convert_to_txt.bat           # Windows batch file for ST to TXT conversion
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.6 or later
- Windows environment (for .bat files, though the Python scripts work cross-platform)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/SANHAJIFX/plc-pdf-to-txt-converter.git
   cd plc-pdf-to-txt-converter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## 📝 Usage

### Directory Structure Setup

Before starting, create a directory structure:

```
/
├── TIA_PDFS/                      # Place your PLC PDFs here
├── ConvertedProgram/              # Output for structured text files (created automatically)
└── PlainTextFiles/                # Output for final text files (created automatically)
```

### Step 1: Convert PDFs to Structured Text

1. Place your TIA Portal exported PDFs in the `TIA_PDFS` directory
2. Run the conversion script:
   - **Using the batch file (Windows)**:
     Double-click `convert_pdfs.bat` or run it from the command line
   - **Using Python directly**:
     ```
     python pdf_to_structured_text.py
     ```
3. The structured text files will be saved in the `ConvertedProgram` directory, organized by block type

### Step 2: Convert Structured Text to Plain Text (under 2MB)

1. Run the second conversion script:
   - **Using the batch file (Windows)**:
     Double-click `convert_to_txt.bat` or run it from the command line
   - **Using Python directly**:
     ```
     python convert_to_txt.py
     ```
2. The plain text files will be saved in the `PlainTextFiles` directory

## 📈 Development Process

### Version History

#### v1.0: Basic PDF Text Extraction
- Initial implementation of PDF text extraction
- Basic organization of extracted content

#### v1.1: Structured Text Conversion
- Added structured format preservation
- Implemented network identification and formatting
- Added specialized handling for different block types

#### v1.2: Enhanced Structure & Metadata
- Added metadata extraction and preservation
- Implemented LAD/FBD diagram text representation
- Added specialized instruction formatting

#### v1.3: File Size Management
- Added functionality to split files into parts under 2MB
- Implemented navigation headers and footers between parts
- Developed intelligent file naming conventions

#### v1.4: Robustness & Fine-tuning
- Enhanced error handling for different file formats and encodings
- Optimized file splitting algorithm to handle edge cases
- Added part size verification and emergency splitting if needed

## 🔍 Limitations

- **Graphical Elements**: Complex graphical elements from the PDF may have limited representation in text format
- **Custom Instructions**: Some highly specialized or custom instructions may require manual review
- **PDF Quality**: The extraction quality depends on the PDF's structure and formatting
- **Language Specificity**: The tool is optimized for TIA Portal exports and may require adjustments for other PLC programming environments
- **Large Datasets**: Very large programs may require significant processing time

## 🔮 Future Improvements

- **Cross-platform GUI**: Create a graphical user interface for easier operation
- **Enhanced Diagram Representation**: Improve the text representation of complex diagrams
- **Bidirectional Conversion**: Add support for converting text back to importable formats
- **Optimization**: Improve processing speed for very large PDF files
- **Additional PLC Platforms**: Extend support to other PLC programming environments
- **Structured Comparison**: Add tools to compare different versions of programs
- **Code Analysis**: Implement basic code analysis and validation

## 📊 Performance

Benchmarks based on test dataset:
- Successfully converted 27 PLC program PDFs to structured text format
- Split larger files into multiple parts, resulting in 55 total text files
- All files are under 2MB as required (largest file is approximately 1.76MB)
- Total size of all converted files is approximately 51.85MB

## 🙏 Acknowledgments

- This tool uses [PyPDF2](https://github.com/py-pdf/PyPDF2) for PDF processing
- Inspired by the need for better tools to work with industrial control systems

## 📄 License

This project is available as open source under the terms of the MIT License. See the LICENSE file for more details.

---

*This tool is provided to help engineers and technicians work with PLC program documentation. It maintains program structure and logic while making the content more accessible and easier to analyze.*