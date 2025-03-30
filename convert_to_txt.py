import os
import shutil
from pathlib import Path

def convert_st_to_txt_files(source_dir, output_dir, max_file_size_mb=2):
    """Convert all .st files to .txt files and place them in a single folder."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Convert max file size to bytes, leaving an even larger margin for headers/footers
    # Use 85% of max size to account for headers and footers and any unexpected factors
    max_file_size = int(max_file_size_mb * 1024 * 1024 * 0.85)
    
    # Create output directory if it doesn't exist
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    # Find all .st files recursively
    st_files = []
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith('.st'):
                st_files.append(os.path.join(root, file))
    
    print(f"Found {len(st_files)} .st files to convert")
    total_parts = 0
    
    # Convert each file to .txt
    for st_file in st_files:
        st_path = Path(st_file)
        rel_path = st_path.relative_to(source_path) if st_path.is_relative_to(source_path) else st_path.name
        
        # Create txt filename with block type prefix to avoid name collisions
        block_type = st_path.parent.name
        base_filename = f"{block_type}_{st_path.stem}"
        
        # Check file size
        file_size = os.path.getsize(st_path)
        
        if file_size <= max_file_size:
            # File is small enough, just copy it
            txt_filename = f"{base_filename}.txt"
            txt_path = output_path / txt_filename
            shutil.copy2(st_path, txt_path)
            print(f"Converted {rel_path} to {txt_filename} ({file_size / (1024 * 1024):.2f} MB)")
        else:
            # File is too large, split it into parts
            # Read the whole file
            try:
                with open(st_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with a different encoding if utf-8 fails
                with open(st_path, 'r', encoding='latin1') as f:
                    content = f.read()
            
            # Split into lines
            lines = content.splitlines()
            total_lines = len(lines)
            
            # Estimate header/footer size (in bytes)
            header_size = len(f"// Part X of Y - {base_filename}\n// Original file: {rel_path}\n// IMPORTANT: This is a continuation from part X. Previous content should be reviewed first.\n// " + "=" * 75 + "\n\n")
            footer_size = len("\n\n// " + "=" * 30 + "\n// End of part X. Continues in part X+1.\n// " + "=" * 30)
            
            # Calculate how many lines we can fit in each part
            # First, estimate average bytes per line
            avg_bytes_per_line = file_size / total_lines if total_lines > 0 else 100
            
            # Add 20% more to avg_bytes_per_line to account for potential variation
            avg_bytes_per_line *= 1.2
            
            # Calculate max lines per part, leaving room for header and footer
            max_lines_per_part = int((max_file_size - header_size - footer_size) / avg_bytes_per_line)
            
            # Calculate number of parts needed
            num_parts = (total_lines + max_lines_per_part - 1) // max_lines_per_part
            total_parts += num_parts
            
            print(f"Splitting {rel_path} into {num_parts} parts (total size: {file_size / (1024 * 1024):.2f} MB)")
            
            # Process each part
            for part in range(num_parts):
                part_filename = f"{base_filename}_part{part+1:02d}.txt"
                part_path = output_path / part_filename
                
                # Calculate start and end indices for this part
                start_idx = part * max_lines_per_part
                # For the last part, include all remaining lines
                end_idx = min((part + 1) * max_lines_per_part, total_lines)
                
                # Write the part file
                with open(part_path, 'w', encoding='utf-8') as f:
                    # Add a header to indicate it's a part file
                    f.write(f"// Part {part+1} of {num_parts} - {base_filename}\n")
                    f.write(f"// Original file: {rel_path}\n")
                    if part > 0:
                        f.write(f"// IMPORTANT: This is a continuation from part {part}. Previous content should be reviewed first.\n")
                    f.write("// " + "=" * 75 + "\n\n")
                    
                    # Write the content for this part
                    part_content = "\n".join(lines[start_idx:end_idx])
                    f.write(part_content)
                    
                    # Add a footer for non-final parts
                    if part < num_parts - 1:
                        f.write("\n\n// " + "=" * 30 + "\n")
                        f.write(f"// End of part {part+1}. Continues in part {part+2}.\n")
                        f.write("// " + "=" * 30)
                
                part_size = os.path.getsize(part_path) / (1024 * 1024)
                print(f"  Created {part_filename} ({part_size:.2f} MB, lines {start_idx+1}-{end_idx})")
                
                # Force additional split if still over the limit
                if part_size > max_file_size_mb:
                    print(f"  WARNING: {part_filename} is {part_size:.2f} MB, which exceeds the {max_file_size_mb} MB limit!")
                    print(f"  Forcibly splitting this part into smaller chunks...")
                    
                    # Delete the oversized file
                    os.remove(part_path)
                    
                    # Read the content again 
                    with open(st_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Calculate how many sub-parts we need
                    sub_parts = int(part_size / max_file_size_mb) + 1
                    lines_per_sub_part = (end_idx - start_idx) // sub_parts
                    
                    # Create sub-parts
                    for sub_part in range(sub_parts):
                        sub_filename = f"{base_filename}_part{part+1:02d}_{chr(97 + sub_part)}.txt"
                        sub_path = output_path / sub_filename
                        
                        sub_start = start_idx + (sub_part * lines_per_sub_part)
                        sub_end = start_idx + ((sub_part + 1) * lines_per_sub_part) if sub_part < sub_parts - 1 else end_idx
                        
                        with open(sub_path, 'w', encoding='utf-8') as f:
                            f.write(f"// Part {part+1}.{sub_part+1} of {num_parts} - {base_filename}\n")
                            f.write(f"// Original file: {rel_path}\n")
                            f.write(f"// IMPORTANT: This is a sub-part {chr(97 + sub_part)} of part {part+1}.\n")
                            f.write("// " + "=" * 75 + "\n\n")
                            
                            sub_content = "\n".join(lines[sub_start:sub_end])
                            f.write(sub_content)
                            
                            if sub_part < sub_parts - 1:
                                f.write("\n\n// " + "=" * 30 + "\n")
                                f.write(f"// End of sub-part {chr(97 + sub_part)}. Continues in sub-part {chr(97 + sub_part + 1)}.\n")
                                f.write("// " + "=" * 30)
                        
                        sub_size = os.path.getsize(sub_path) / (1024 * 1024)
                        print(f"    Created {sub_filename} ({sub_size:.2f} MB, lines {sub_start+1}-{sub_end})")
    
    print(f"Conversion completed! All files are in the {output_dir} directory")
    print(f"Total files created: {sum(1 for f in os.listdir(output_path) if f.endswith('.txt'))}")
    print(f"Total parts created for large files: {total_parts}")

if __name__ == "__main__":
    SOURCE_DIRECTORY = "ConvertedProgram"
    OUTPUT_DIRECTORY = "PlainTextFiles"
    MAX_FILE_SIZE_MB = 2  # Maximum file size in MB
    
    # Clean output directory if it exists
    if os.path.exists(OUTPUT_DIRECTORY):
        print(f"Cleaning output directory {OUTPUT_DIRECTORY}...")
        for file in os.listdir(OUTPUT_DIRECTORY):
            file_path = os.path.join(OUTPUT_DIRECTORY, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    convert_st_to_txt_files(SOURCE_DIRECTORY, OUTPUT_DIRECTORY, MAX_FILE_SIZE_MB)