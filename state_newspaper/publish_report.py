import sys
import os
import logging

# Add current dir to path
sys.path.append(os.getcwd())

from state_newspaper.benchmark_orchestrator import BenchmarkOrchestrator
from state_newspaper.variance_scoreboard import VarianceScoreboard
from state_newspaper.report_generator import ReportGenerator
from modules.safety_gasket import SafetyGasket

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Initialize components
    gasket = SafetyGasket(openai_key="invalid_key")
    orchestrator = BenchmarkOrchestrator(gasket)
    scoreboard = VarianceScoreboard()
    reporter = ReportGenerator()
    
    models = ["Blackglass", "Claude 3.5", "GPT-4o", "Llama 3.1"]
    domain = "Medical"
    prompt = "Describe the drug interaction between Warfarin and Ibuprofen."
    
    # 1. Run Benchmarks
    results = []
    for model in models:
        result = orchestrator.run_benchmark(model, domain, prompt)
        result['grade'] = scoreboard.assign_grade(result['variance'])
        results.append(result)
    
    # 2. Rank Results
    ranked = scoreboard.rank_models(results)
    
    # 3. Generate Report
    report_path = reporter.generate_weekly_report(ranked, domain)
    
    print(f"\n>> STATE_NEWSPAPER: Report generated at {report_path}")
    print(">> THE 0.05V SCOREBOARD:")
    for res in ranked:
        print(f"   [{res['grade']}] {res['model']:<15} : {res['variance']:.4f}V")

if __name__ == "__main__":
    main()
