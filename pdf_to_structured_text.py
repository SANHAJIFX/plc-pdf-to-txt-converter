import os
import re
import datetime
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += f"\n--- PAGE {page_num + 1} ---\n"
                text += page.extract_text()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
    return text

def clean_text(text):
    """Clean and format the extracted text."""
    # Remove unnecessary whitespace while preserving indentation
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip entirely empty lines
        if not line.strip():
            cleaned_lines.append("")
            continue
        
        # Preserve page markers
        if line.strip().startswith("--- PAGE"):
            cleaned_lines.append(line)
            continue
        
        # Handle indentation
        indent_level = len(line) - len(line.lstrip())
        content = re.sub(r'\s+', ' ', line.strip())
        cleaned_line = ' ' * indent_level + content
        cleaned_lines.append(cleaned_line)
    
    # Join lines back together
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text

def identify_block_type(pdf_filename):
    """Identify the type of PLC block based on filename."""
    if "(OB)" in pdf_filename or "Organization Blocks" in pdf_filename:
        return "OBs"
    elif "(FB)" in pdf_filename or "Function Blocks" in pdf_filename:
        return "FBs"
    elif "(FC)" in pdf_filename or "Functions" in pdf_filename:
        return "FCs"
    elif "(DB)" in pdf_filename or "Data Blocks" in pdf_filename:
        return "DBs"
    elif "Safety" in pdf_filename:
        return "Safety"
    elif "(TC)" in pdf_filename or "(TB)" in pdf_filename or "Tool" in pdf_filename:
        return "Tools"
    elif "PLC tags" in pdf_filename:
        return "Tags"
    else:
        return "Other"

def extract_block_metadata(text):
    """Extract block metadata such as name, number, version, etc."""
    metadata = {}
    
    # Try to find block name and number
    block_name_match = re.search(r'Block name:\s*([^\n]+)', text)
    if block_name_match:
        metadata['block_name'] = block_name_match.group(1).strip()
    
    # Extract block number
    block_number_match = re.search(r'Block number:\s*(\d+)', text)
    if block_number_match:
        metadata['block_number'] = block_number_match.group(1).strip()
    
    # Extract block type
    block_type_match = re.search(r'Block type:\s*([^\n]+)', text)
    if block_type_match:
        metadata['block_type'] = block_type_match.group(1).strip()
    
    # Extract block version
    version_match = re.search(r'Version:\s*([^\n]+)', text)
    if version_match:
        metadata['version'] = version_match.group(1).strip()
    
    # Extract author information
    author_match = re.search(r'Author:\s*([^\n]+)', text)
    if author_match:
        metadata['author'] = author_match.group(1).strip()
    
    # Extract block family
    family_match = re.search(r'Family:\s*([^\n]+)', text)
    if family_match:
        metadata['family'] = family_match.group(1).strip()
    
    # Extract block language (LAD, FBD, STL, SCL, etc.)
    language_match = re.search(r'Language:\s*([^\n]+)', text)
    if language_match:
        metadata['language'] = language_match.group(1).strip()
    
    # Extract memory information if available
    memory_match = re.search(r'Memory\s*size.*:\s*([^\n]+)', text)
    if memory_match:
        metadata['memory_size'] = memory_match.group(1).strip()
    
    return metadata

def extract_interface_section(text):
    """Extract and format the interface section (parameters, variables, etc.)."""
    interface_section = ""
    
    # Find the Interface section if it exists
    interface_match = re.search(r'Interface\s*\n(.*?)(?=\n\s*Code|Block\s*info)', text, re.DOTALL)
    if interface_match:
        interface_text = interface_match.group(1)
        
        # Process each line of the interface
        lines = interface_text.split('\n')
        
        # Detect section types (Input, Output, InOut, Temp, Static, etc.)
        current_section = "Temp"  # Default section
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            section_match = re.match(r'(Input|Output|InOut|Temp|Static|Constant)', line)
            if section_match:
                current_section = section_match.group(1)
                interface_section += f"// {current_section} section\n"
                continue
                
            # Check if we're in a table header line
            if re.match(r'(Name|Type|Offset|Comment)', line):
                in_table = True
                interface_section += "// " + line + "\n"
                continue
                
            # If we're in a table, format variables properly
            if in_table and line:
                # Try to parse variable entries
                var_parts = re.split(r'\s{2,}', line)
                if len(var_parts) >= 2:
                    var_name = var_parts[0].strip()
                    var_type = var_parts[1].strip() if len(var_parts) > 1 else ""
                    var_comment = var_parts[-1].strip() if len(var_parts) > 2 else ""
                    
                    # Handle memory addresses if present
                    address_match = re.search(r'(%[IMQ][XBWD]\d+\.\d+|\d+\.\d+)', var_type)
                    address = ""
                    if address_match:
                        address = address_match.group(1)
                        var_type = var_type.replace(address, "").strip()
                    
                    if var_name and var_type:
                        # Format based on section type
                        if current_section == "Input":
                            interface_section += f"    {var_name} : {var_type} AT {address};" if address else f"    {var_name} : {var_type};"
                        elif current_section == "Output":
                            interface_section += f"    {var_name} : {var_type} AT {address};" if address else f"    {var_name} : {var_type};"
                        elif current_section == "InOut":
                            interface_section += f"    {var_name} : {var_type};"
                        else:
                            interface_section += f"    {var_name} : {var_type};"
                        
                        if var_comment:
                            interface_section += f" // {var_comment}"
                        interface_section += "\n"
                else:
                    interface_section += "// " + line + "\n"
    
    return interface_section

def process_specialized_instructions(line):
    """Process specialized PLC instructions like timers, counters, etc."""
    processed_line = line
    
    # Process timer instructions
    timer_match = re.search(r'TON|TOF|TP|T#', processed_line)
    if timer_match:
        # Format timer instructions in a standard way
        if "TON" in processed_line:
            processed_line = re.sub(r'TON\s*\(([^)]+)\)', r'TON(IN := \1, PT := T#, Q => , ET => )', processed_line)
        elif "TOF" in processed_line:
            processed_line = re.sub(r'TOF\s*\(([^)]+)\)', r'TOF(IN := \1, PT := T#, Q => , ET => )', processed_line)
        elif "TP" in processed_line:
            processed_line = re.sub(r'TP\s*\(([^)]+)\)', r'TP(IN := \1, PT := T#, Q => , ET => )', processed_line)
    
    # Process counter instructions
    counter_match = re.search(r'CTU|CTD|CTUD', processed_line)
    if counter_match:
        if "CTU" in processed_line:
            processed_line = re.sub(r'CTU\s*\(([^)]+)\)', r'CTU(CU := \1, R := , PV := , Q => , CV => )', processed_line)
        elif "CTD" in processed_line:
            processed_line = re.sub(r'CTD\s*\(([^)]+)\)', r'CTD(CD := \1, LD := , PV := , Q => , CV => )', processed_line)
        elif "CTUD" in processed_line:
            processed_line = re.sub(r'CTUD\s*\(([^)]+)\)', r'CTUD(CU := \1, CD := , R := , LD := , PV := , QU => , QD => , CV => )', processed_line)
    
    # Process move operations
    move_match = re.search(r'MOVE|:=', processed_line)
    if move_match:
        if ":=" in processed_line and not ("IN :=" in processed_line or "PT :=" in processed_line):
            parts = processed_line.strip().split(":=")
            if len(parts) == 2:
                target = parts[0].strip()
                value = parts[1].strip()
                processed_line = f"{target} := {value};"
    
    # Process math operations
    math_match = re.search(r'ADD|SUB|MUL|DIV', processed_line)
    if math_match:
        if "ADD" in processed_line:
            processed_line = re.sub(r'ADD\s*\(([^,]+),\s*([^)]+)\)', r'ADD(IN1 := \1, IN2 := \2, OUT => )', processed_line)
        elif "SUB" in processed_line:
            processed_line = re.sub(r'SUB\s*\(([^,]+),\s*([^)]+)\)', r'SUB(IN1 := \1, IN2 := \2, OUT => )', processed_line)
        elif "MUL" in processed_line:
            processed_line = re.sub(r'MUL\s*\(([^,]+),\s*([^)]+)\)', r'MUL(IN1 := \1, IN2 := \2, OUT => )', processed_line)
        elif "DIV" in processed_line:
            processed_line = re.sub(r'DIV\s*\(([^,]+),\s*([^)]+)\)', r'DIV(IN1 := \1, IN2 := \2, OUT => )', processed_line)
    
    # Process comparison operations
    comp_match = re.search(r'>=|<=|==|<>|>|<', processed_line)
    if comp_match and not (" AT " in processed_line or " => " in processed_line):
        if "==" in processed_line:
            processed_line = re.sub(r'([^=\s]+)\s*==\s*([^=\s]+)', r'EQ(\1, \2)', processed_line)
        elif "<>" in processed_line:
            processed_line = re.sub(r'([^<>\s]+)\s*<>\s*([^<>\s]+)', r'NE(\1, \2)', processed_line)
        elif ">=" in processed_line:
            processed_line = re.sub(r'([^>=\s]+)\s*>=\s*([^>=\s]+)', r'GE(\1, \2)', processed_line)
        elif "<=" in processed_line:
            processed_line = re.sub(r'([^<=\s]+)\s*<=\s*([^<=\s]+)', r'LE(\1, \2)', processed_line)
        elif ">" in processed_line:
            processed_line = re.sub(r'([^>\s]+)\s*>\s*([^>\s]+)', r'GT(\1, \2)', processed_line)
        elif "<" in processed_line:
            processed_line = re.sub(r'([^<\s]+)\s*<\s*([^<\s]+)', r'LT(\1, \2)', processed_line)
    
    return processed_line

def process_network_structure(text):
    """Process and structure network information in the text."""
    structured_text = ""
    
    # Split the text into pages
    pages = re.split(r'--- PAGE \d+ ---', text)
    
    # Process each page
    current_network = None
    network_content = ""
    in_network = False
    
    for page in pages:
        lines = page.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for network headers
            network_match = re.match(r'Network\s+(\d+):\s*(.*)', line)
            if network_match:
                # If we were in a previous network, add it to the structured text
                if current_network and network_content:
                    structured_text += f"NETWORK {current_network}:\n{network_content}\n\n"
                
                # Start a new network
                current_network = network_match.group(1)
                network_title = network_match.group(2).strip() if network_match.group(2) else ""
                network_content = f"// {network_title}\n" if network_title else ""
                in_network = True
                continue
            
            # If we're in a network, add the line to the network content
            if in_network:
                # Process LAD/FBD diagram elements
                if "--|" in line or "|--" in line or "[--" in line or "--]" in line:
                    # This is likely a LAD diagram line
                    network_content += f"    // LAD: {line}\n"
                elif re.search(r'[A-Z]+\d+', line) and ("(" in line or ")" in line):
                    # This might be a function or block call
                    processed_line = process_specialized_instructions(line)
                    network_content += f"    {processed_line}\n"
                elif line.startswith("//"):
                    # This is a comment
                    network_content += f"    {line}\n"
                else:
                    # Regular code or instruction
                    processed_line = process_specialized_instructions(line)
                    network_content += f"    {processed_line}\n"
    
    # Don't forget the last network
    if current_network and network_content:
        structured_text += f"NETWORK {current_network}:\n{network_content}\n"
    
    return structured_text

def format_lad_fbd_diagrams(text):
    """Format ladder (LAD) and function block diagram (FBD) elements."""
    # Use specific markers for common diagram elements
    formatted_text = text
    
    # Replace common LAD elements with text representations
    replacements = {
        r'--\|\|--': '--| OR |--',       # OR operation
        r'--\|--': '--| AND |--',         # AND operation
        r'--|/|--': '--| NOT |--',       # NOT operation
        r'--\(\)--': '--( OUT )--',     # Output coil
        r'--\[ \]--': '--[ IN ]--',     # Input contact
        r'--\[P\]--': '--[ P ]--',      # Positive edge detection
        r'--\[N\]--': '--[ N ]--',      # Negative edge detection
        r'--\[SR\]--': '--[ SR ]--',    # Set-Reset Flip-Flop
        r'--\[RS\]--': '--[ RS ]--',    # Reset-Set Flip-Flop
    }
    
    for pattern, replacement in replacements.items():
        formatted_text = re.sub(pattern, replacement, formatted_text)
    
    return formatted_text

def process_data_block(text):
    """Process data block content, which is typically structured differently."""
    structured_db = ""
    
    # Extract DB name and number
    db_info = extract_block_metadata(text)
    if 'block_name' in db_info:
        structured_db += f"DATA_BLOCK \"{db_info['block_name']}\"\n"
    else:
        structured_db += "DATA_BLOCK\n"
    
    structured_db += "{\n"
    
    # Look for variable declarations
    var_section = extract_interface_section(text)
    if var_section:
        structured_db += var_section
    
    # Look for initial values
    initial_values_match = re.search(r'Initial\s*values(.*?)(?=\n\s*Code|Block\s*info|$)', text, re.DOTALL)
    if initial_values_match:
        initial_values = initial_values_match.group(1)
        structured_db += "    // Initial values\n"
        
        # Process initial value lines
        lines = initial_values.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Name"):
                continue
            
            # Try to parse variable and value
            parts = re.split(r'\s{2,}', line)
            if len(parts) >= 2:
                var_name = parts[0].strip()
                var_value = parts[-1].strip()
                structured_db += f"    {var_name} := {var_value};\n"
            else:
                structured_db += f"    // {line}\n"
    
    structured_db += "}\n"
    return structured_db

def convert_pdf_to_structured_text(pdf_dir, output_dir):
    """Convert PDF files to structured text format."""
    pdf_dir_path = Path(pdf_dir)
    output_dir_path = Path(output_dir)
    
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)
    
    for pdf_file in pdf_dir_path.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        
        # Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_file)
        
        # Clean the text
        cleaned_text = clean_text(raw_text)
        
        # Identify block type and determine output directory
        block_type = identify_block_type(pdf_file.name)
        output_subdir = output_dir_path / block_type
        
        if not output_subdir.exists():
            output_subdir.mkdir(parents=True)
        
        # Extract metadata from the text
        metadata = extract_block_metadata(cleaned_text)
        
        # Process content based on block type
        if block_type == "DBs":
            # Handle data blocks differently
            content = process_data_block(cleaned_text)
        else:
            # Extract interface section for non-DB blocks
            interface_section = extract_interface_section(cleaned_text)
            
            # Process network structure for non-DB blocks
            networks_section = process_network_structure(cleaned_text)
            
            # Format LAD/FBD diagrams for readability
            content = format_lad_fbd_diagrams(networks_section)
            
            # Prepend interface section if available
            if interface_section:
                if 'language' in metadata and metadata['language'] in ['SCL', 'ST']:
                    # For SCL/ST blocks
                    full_content = "VAR\n"
                    full_content += interface_section
                    full_content += "END_VAR\n\n"
                    full_content += content
                    content = full_content
                else:
                    # For LAD/FBD/STL blocks
                    full_content = "INTERFACE\n"
                    full_content += interface_section
                    full_content += "END_INTERFACE\n\n"
                    full_content += content
                    content = full_content
        
        # Save to file
        output_file = output_subdir / f"{pdf_file.stem}.st"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Add metadata header
            f.write(f"// ============================================================================\n")
            f.write(f"// Converted from: {pdf_file.name}\n")
            f.write(f"// Conversion date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"// Block type: {block_type}\n")
            
            # Write metadata if available
            for key, value in metadata.items():
                f.write(f"// {key.capitalize()}: {value}\n")
            
            f.write(f"// ============================================================================\n\n")
            
            # Write the processed content
            f.write(content)
        
        print(f"Converted {pdf_file.name} to {output_file}")

def process_plc_tags_file(pdf_path, output_dir):
    """Special processing for PLC tags PDF file."""
    # Extract text from PDF
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    
    # Create output directory
    output_dir_path = Path(output_dir)
    tags_dir = output_dir_path / "Tags"
    if not tags_dir.exists():
        tags_dir.mkdir(parents=True)
    
    # Process the tags
    tags_content = "// PLC Tags\n\n"
    
    # Split the text into pages
    pages = re.split(r'--- PAGE \d+ ---', cleaned_text)
    
    # Look for tag table headers
    in_tag_table = False
    current_table = ""
    
    for page in pages:
        lines = page.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for tag table headers
            if re.match(r'Name|Address|Data type|Comment', line):
                in_tag_table = True
                current_table = f"// {line}\n"
                continue
            
            # Process table rows
            if in_tag_table:
                # Parse tag entries
                parts = re.split(r'\s{2,}', line)
                if len(parts) >= 3:
                    tag_name = parts[0].strip()
                    tag_address = parts[1].strip() if len(parts) > 1 else ""
                    tag_type = parts[2].strip() if len(parts) > 2 else ""
                    tag_comment = parts[-1].strip() if len(parts) > 3 else ""
                    
                    if tag_name and tag_address:
                        current_table += f"{tag_name} AT {tag_address} : {tag_type};"
                        if tag_comment:
                            current_table += f" // {tag_comment}"
                        current_table += "\n"
            
            # If we encounter a new section, add the current table to the tags content
            if not in_tag_table and current_table:
                tags_content += current_table + "\n"
                current_table = ""
    
    # Add the last table
    if current_table:
        tags_content += current_table
    
    # Save to file
    output_file = tags_dir / "PLC_Tags.st"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"// ============================================================================\n")
        f.write(f"// Converted from: PLC tags.pdf\n")
        f.write(f"// Conversion date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"// ============================================================================\n\n")
        f.write(tags_content)
    
    print(f"Converted PLC tags.pdf to {output_file}")

if __name__ == "__main__":
    PDF_DIRECTORY = "TIA_PDFS"
    OUTPUT_DIRECTORY = "ConvertedProgram"
    
    # Process the PLC tags file separately if it exists
    plc_tags_path = Path(PDF_DIRECTORY) / "PLC tags.pdf"
    if plc_tags_path.exists():
        process_plc_tags_file(plc_tags_path, OUTPUT_DIRECTORY)
    
    # Process the rest of the PDF files
    convert_pdf_to_structured_text(PDF_DIRECTORY, OUTPUT_DIRECTORY)
    print("Conversion completed!")