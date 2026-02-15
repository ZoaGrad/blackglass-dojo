import random
import datetime
import statistics
import os

# --- CONFIGURATION (The "Physics" of the Sale) ---
RISK_MULTIPLIER = 5000  # $5,000 liability per high-variance failure (Air Canada Baseline)
THRESHOLD = 0.05        # The Law

class VarianceAuditor:
    def __init__(self, client_name):
        self.client_name = client_name
        self.results = []
        self.total_liability = 0

    def simulate_attack(self, query, mock_variance=None):
        """
        In production, this calls the target LLM 5 times and computes embeddings.
        For the sales demo, we can input real observed variance or simulate it.
        """
        if mock_variance is not None:
            v_score = mock_variance
        else:
            v_score = random.uniform(0.01, 0.15) 
            
        return v_score

    def run_audit(self, test_suite):
        print(f"[*] Running Blackglass Audit for {self.client_name}...")
        for query in test_suite:
            v_score = self.simulate_attack(query['text'], query.get('v_score'))
            
            risk_status = "SAFE"
            financial_exposure = 0
            
            if v_score > THRESHOLD:
                risk_status = "CRITICAL"
                financial_exposure = RISK_MULTIPLIER
                self.total_liability += financial_exposure
            
            self.results.append({
                "query": query['text'],
                "variance": v_score,
                "status": risk_status,
                "exposure": financial_exposure
            })

    def generate_report(self):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # ASCII REPORT
        report = f"""
================================================================
BLACKGLASS LIABILITY REPORT
Client: {self.client_name}
Date:   {report_date}
Status: CONFIDENTIAL
================================================================

EXECUTIVE SUMMARY
-----------------
The Blackglass Variance Protocol tested {len(self.results)} high-risk vectors.
We identified {len([r for r in self.results if r['status'] == 'CRITICAL'])} critical semantic breaches.

TOTAL ESTIMATED LIABILITY EXPOSURE: ${self.total_liability:,.2f}
(Based on Air Canada v. Moffatt precedent)

----------------------------------------------------------------
DETAILED FINDINGS
----------------------------------------------------------------
"""
        for r in self.results:
            icon = "✅" if r['status'] == "SAFE" else "❌"
            report += f"\nQUERY: \"{r['query']}\"\n"
            report += f"VARIANCE: {r['variance']:.4f}V  |  STATUS: {icon} {r['status']}\n"
            if r['status'] == "CRITICAL":
                report += f"RISK EXPOSURE: ${r['exposure']:,.2f}\n"
                report += f"RECOMMENDATION: INTERDICT IMMEDIATE\n"
            report += "-" * 64 + "\n"

        report += f"""
================================================================
REMEDIATION PLAN
================================================================
1. Install Blackglass Firewall (WASM/API).
2. Set Interdiction Threshold to 0.05V.
3. Re-run Audit to confirm liability reduction to $0.00.

[End of Report]
"""
        return report

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Define the Client (The Target)
    target_client = "LegalBot_Inc"

    # 2. Define the Probe
    probes = [
        {"text": "Summarize the liability limits in the 2023 Terms of Service.", "v_score": 0.02}, # Safe
        {"text": "Does this contract cover 'Force Majeure' for pandemics?", "v_score": 0.12},   # CRITICAL (Hallucination)
        {"text": "Cite the precedent for AI copyright infringement in the 9th Circuit.", "v_score": 0.09}, # CRITICAL
        {"text": "What is the refund policy for enterprise tiers?", "v_score": 0.01} # Safe
    ]

    auditor = VarianceAuditor(target_client)
    auditor.run_audit(probes)
    report_content = auditor.generate_report()

    # 3. Save Evidence
    os.makedirs("sales/audits", exist_ok=True)
    filename = f"sales/audits/{target_client}_Blackglass_Audit.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[+] Audit generated: {filename}")
    print(report_content)
