import os
import json
import time
from colorama import Fore, Style, init

init(autoreset=True)

# Paths to Continuum telemetry
SENTINEL_STATUS = r"c:\Users\colem\blackglass-sentinel\sentinel_status.json"
VARIANCE_REPORT = r"c:\Users\colem\Code\blackglass-variance-core\VARIANCE_REPORT.md"
SHARD_ALPHA_RESULTS = r"c:\Users\colem\Code\blackglass-shard-alpha\results.json"

def get_si_color(si):
    if si > 0.7: return Fore.GREEN
    if si > 0.3: return Fore.YELLOW
    return Fore.RED

def read_sentinel():
    if not os.path.exists(SENTINEL_STATUS): return "OFFLINE", 0.0, Fore.RED
    with open(SENTINEL_STATUS, 'r') as f:
        data = json.load(f)
        status = data.get("status", "UNKNOWN")
        si = 1.0 if status == "NOMINAL" else 0.2
        color = Fore.GREEN if status == "NOMINAL" else Fore.RED
        return status, si, color

def read_variance_core():
    if not os.path.exists(VARIANCE_REPORT): return "OFFLINE", 0.0, Fore.RED
    with open(VARIANCE_REPORT, 'r') as f:
        content = f.read()
        # Parse SI from markdown
        import re
        si_match = re.search(r"Stability Index \(SI\):\*\* ([\d.]+)", content)
        si = float(si_match.group(1)) if si_match else 0.0
        status = "HYPER-COHERENT" if si > 0.7 else ("VOLATILE" if si > 0.3 else "BREACH")
        return status, si, get_si_color(si)

def read_shard_alpha():
    if not os.path.exists(SHARD_ALPHA_RESULTS): return "IDLE", 1.0, Fore.GREEN
    with open(SHARD_ALPHA_RESULTS, 'r') as f:
        data = json.load(f)
        dd = data.get("max_drawdown", 0.0)
        si = max(0.0, 1.0 - (dd / 0.05)) # Hard stop at 5%
        status = "TRADING" if si > 0.0 else "HALTED"
        return status, si, get_si_color(si)

def render_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Style.BRIGHT + Fore.CYAN + "┌" + "─" * 45 + "┐")
    print(Style.BRIGHT + Fore.CYAN + "│" + "  BLACKGLASS CONTINUUM // SI DASHBOARD       ".center(45) + "│")
    print(Style.BRIGHT + Fore.CYAN + "├" + "─" * 45 + "┤")
    
    s_status, s_si, s_color = read_sentinel()
    v_status, v_si, v_color = read_variance_core()
    a_status, a_si, a_color = read_shard_alpha()
    
    def bar(si):
        filled = int(si * 10)
        return "█" * filled + "░" * (10 - filled)

    print(f"│  SENTINEL    [SI: {s_si:.2f}] {s_color}{bar(s_si)} {s_status.ljust(10)}{Fore.CYAN}│")
    print(f"│  VAR_CORE    [SI: {v_si:.2f}] {v_color}{bar(v_si)} {v_status.ljust(10)}{Fore.CYAN}│")
    print(f"│  SHARD_ALPHA [SI: {a_si:.2f}] {a_color}{bar(a_si)} {a_status.ljust(10)}{Fore.CYAN}│")
    
    print(Style.BRIGHT + Fore.CYAN + "├" + "─" * 45 + "┤")
    # Global state interdiction
    if s_si < 0.3:
        print(Style.BRIGHT + Fore.RED + "│" + " !! GLOBAL CIRCUIT BREAKER ACTIVE !! ".center(45) + "│")
        print(Style.BRIGHT + Fore.RED + "│" + " FATIGUE BREACH DETECTED -> LOCKING TRADES ".center(45) + "│")
    else:
        print(Fore.GREEN + "│" + " CONTINUUM NOMINAL // ALL SYSTEMS GO ".center(45) + "│")
        
    print(Style.BRIGHT + Fore.CYAN + "└" + "─" * 45 + "┘")
    print(f"Last Poll: {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    try:
        while True:
            render_dashboard()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nTelemetry decoupled.")
