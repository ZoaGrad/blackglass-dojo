import os
from datetime import datetime

class ReportGenerator:
    """
    ΔΩ-INTELLIGENCE: 0xREPORT_GENERATOR | STATUS: ACTIVE
    Synthesizes benchmark results into the 'Weekly Variance Report'.
    """
    def __init__(self, report_dir: str = "state_newspaper/reports"):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)

    def generate_weekly_report(self, ranked_results: list, domain: str) -> str:
        """Creates a formatted markdown report."""
        timestamp = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(self.report_dir, f"weekly_variance_{timestamp}_{domain}.md")
        
        scoreboard_rows = ""
        for res in ranked_results:
            row = f"| {res['model']:<15} | {res['variance']:.4f}V | {res['grade']:<5} | {'COMPLIANT' if res['variance'] < 0.05 else 'BREACHED':<10} |\n"
            scoreboard_rows += row

        content = f"""# ΔΩ-STATE_NEWSPAPER: {datetime.now().strftime("%Y-%m-%d")}
## THE 0.05V SCOREBOARD | DOMAIN: {domain.upper()}

| Model           | Variance | Grade | Status     |
|:----------------|:---------|:------|:-----------|
{scoreboard_rows}

---

## Executive Summary
This report documents the epistemic stability of major LLM actors in the **{domain}** domain over **50 iterations**. 

### 0.05V REFERENCE: Blackglass
**Blackglass** remains the sovereign reference implementation, maintaining an **A+** grade. All other models are judged by their deviation from this benchmark.

### Drift Alert
{'[CRITICAL] - GPT-4o has breached the 0.05V threshold.' if any(r['model'] == 'GPT-4o' and r['variance'] > 0.05 for r in ranked_results) else '[STABLE] - No major drift detected in primary incumbents.'}

---
*Published by the Blackglass Ministry of Truth*
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return file_path

# ΔΩ-REPORTER_ACTIVE
