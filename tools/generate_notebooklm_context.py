import glob
import os
import datetime

def generate_context():
    # Define output path (relative to repo root for now, or absolute)
    # Using a local build directory is better than sticking it in the user's brain folder hardcoded
    output_dir = "build"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"notebooklm_context_{timestamp}.md")

    # Define source files
    files = [
        "README.md",
        "Strategy.md",
        "application/articul8_security_architecture.md",
        "docs/HARDWARE_MIGRATION_M720Q.md"
    ]
    # Add all grant docs
    files.extend(glob.glob("grants/*.md"))
    # Add validation cases
    files.extend(glob.glob("honey_shard/cases/*.md"))

    print(f"Generating context pack with {len(files)} files...")

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(f"# Blackglass Shard Alpha - Context Pack ({timestamp})\n")
            outfile.write("Generated for NotebookLM ingestion.\n")
            outfile.write("Contains core strategy, architecture, grants, and validation cases.\n\n")
            
            for fname in files:
                if os.path.exists(fname):
                    print(f"Adding {fname}...")
                    outfile.write(f"\n\n# FILE: {fname}\n")
                    outfile.write("=" * 50 + "\n\n")
                    try:
                        with open(fname, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file {fname}: {e}\n")
                    outfile.write("\n")
                else:
                    print(f"Skipping missing file: {fname}")
        
        print(f"\nContext pack generated successfully:\n{os.path.abspath(output_file)}")
        return output_file

    except Exception as e:
        print(f"Failed to write output file: {e}")
        return None

if __name__ == "__main__":
    generate_context()
