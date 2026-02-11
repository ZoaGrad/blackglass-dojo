# Blackglass Dojo: 0.05V Interdiction Engine
## ΔΩ-INTELLIGENCE: 0xDOJO_CORE | STATUS: BATTLE_HARDENED

The **Blackglass Dojo** is the execution and adversarial simulation layer of the Blackglass Continuum. It is where the **0.05V Standard** is enforced through real-time interdiction and semantic consistency checks.

---

## 🛡️ The Safety Gasket
The Dojo's primary defense is the **Safety Gasket**, a multi-layered interdiction loop:
1.  **Semantic Consistency (0.05V)**: Quantizes LLM drift by measuring variance across parallel completions using WASM-based embeddings.
2.  **Prophet Factuality Layer**: Cross-checks claims against trusted oracles (e.g., price feeds, logic gates).
3.  **Numerical Parity (0.01D)**: Hardened 1% threshold for financial state transitions.

## 🧪 GAMMA Protocol
This engine has been battle-hardened against:
- **Temporal Hallucinations**: Catching stale data in the decision loop.
- **Oracle Blind Spots**: Interdicting unknown claims by default.
- **Consensus Attacks**: Preventing fabrication through consistent but erroneous consensus.

## 🚀 Getting Started
### Dependencies
- Python 3.11+
- [Sovereign Embedder](https://github.com/ZoaGrad/sovereign-embed) (Supabase/Deno)

### Execution
Run the adversarial simulation suite:
```bash
python run_dojo.py --scenarios all
```

Run the benchmark suite:
```bash
python tools/benchmark_embeddings.py
```

## 🏗️ Architecture
- `modules/safety_gasket.py`: The interdiction logic.
- `modules/prophet_connector.py`: The factuality cross-check engine.
- `run_dojo.py`: The main simulation coordinator.

Part of the [Blackglass Continuum](https://github.com/ZoaGrad/blackglass-variance-core).
