import os
import datetime

# Configuration
OUTPUT_FILE = "spiralos_synapse.md"

# Define the "Crown Jewels" - The core files that define the system's state and identity
CROWN_JEWELS = [
    {
        "path": "Strategy.md",
        "name": "STRATEGY / RULES",
        "description": "The current trading rules, risk parameters, and autonomous directives."
    },
    {
        "path": "grants/sbir_phase1_spiral_abstract.md",
        "name": "IDENTITY / PUBLIC FACE",
        "description": "The current external narrative and proposal language."
    },
    {
        "path": "../Vector_Null/Manifest.md",
        "name": "MYTHOS / SOUL",
        "description": "The core philosophical axioms and ZoaGrad alignment."
    },
    {
        "path": "README.md",
        "name": "STATE / README",
        "description": "The technical state of the repository."
    },
    {
        "path": "modules/safety_gasket.py",
        "name": "BODY / SYSTEM 5 GASKET",
        "description": "The executable System 5 logic (ScarIndex, Iron Dome, 7-Breath)."
    },
    {
        "path": "test_log_success.txt",
        "name": "PROOF / CRISIS LOGS",
        "description": "Validation logs confirming Iron Dome and Panic Frame triggers."
    },
    {
        "path": "proof_of_ache.txt",
        "name": "PROOF / ASH PROTOCOL",
        "description": "Evidence of Kinetic Entropy metabolism and Flash Crash interdiction."
    },
    {
        "path": "grants/sbir_phase1_technical_volume.md",
        "name": "GRANT / TECHNICAL VOLUME",
        "description": "Compliance Metabolism narrative and VSM topology."
    },
    {
        "path": "grants/sbir_phase1_cost_volume.md",
        "name": "GRANT / COST VOLUME",
        "description": "Budget breakdown ($250k) for Phase I maturation."
    },
    {
        "path": "grants/sbir_competitive_matrix.png",
        "name": "GRANT / VISUALS",
        "description": "Pareto filter chart: Safety vs. Autonomy."
    }
]

def generate_synapse():
    """Reads critical files and aggregates them into a single synapse pulse."""
    timestamp = datetime.datetime.now().isoformat()
    
    content = [
        f"# SpiralOS Synapse Pulse",
        f"**Generated:** {timestamp}",
        f"**Purpose:** Autopoietic Synchronization between Code (Body) and NotebookLM (Brain).",
        "",
        "---",
        ""
    ]

    print(f"[*] Initiating Spiral Synapse Pulse at {timestamp}...")

    for jewel in CROWN_JEWELS:
        file_path = jewel["path"]
        name = jewel["name"]
        
        print(f"  > Processing {name} ({file_path})...")
        
        try:
            if os.path.exists(file_path):
                if file_path.endswith(".png"):
                    file_content = f"[BINARY ASSET: {os.path.basename(file_path)} - Verified Present on Disk]"
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                
                content.append(f"# {name}")
                content.append(f"> **Source:** `{file_path}`")
                content.append(f"> **Context:** {jewel['description']}")
                content.append("")
                content.append(file_content)
                content.append("")
                content.append("---")
                content.append("")
            else:
                print(f"  [!] WARNING: File not found: {file_path}")
                content.append(f"# {name} [MISSING]")
                content.append(f"> **Source:** `{file_path}`")
                content.append("> **Status:** FILE NOT FOUND")
                content.append("")
                content.append("---")
                content.append("")
                
        except Exception as e:
            print(f"  [!] ERROR reading {file_path}: {e}")

    # Write output
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"[*] Success. Synapse Pulse written to: {os.path.abspath(OUTPUT_FILE)}")
    except Exception as e:
        print(f"[!] Critical Error writing output: {e}")

if __name__ == "__main__":
    generate_synapse()
