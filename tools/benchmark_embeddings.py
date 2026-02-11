import time
import numpy as np
import json
from fastembed import TextEmbedding

# --- SOVEREIGN BENCHMARK CONFIG ---
MODEL_NAME = 'BAAI/bge-small-en-v1.5' # Default for fastembed, very similar to MiniLM
SAMPLE_TEXTS = [
    "The ETH/USDT price is currently $2,450.12",
    "Ethereum is trading at approximately two thousand four hundred dollars.",
    "A completely unrelated sentence about coffee.",
    "The 0.05V standard is the constitutional backbone of Blackglass."
]

def benchmark_sovereign_embeddings():
    print(f"[BENCHMARK] Loading Sovereign Model: {MODEL_NAME}...")
    start_load = time.time()
    # fastembed uses ONNX for high-speed inference without torch
    model = TextEmbedding(model_name=MODEL_NAME)
    print(f"[BENCHMARK] Model Loaded in {time.time() - start_load:.2f}s")

    print("\n" + "="*50)
    print(f"SOVEREIGN VS. SEMANTIC CONSISTENCY (N={len(SAMPLE_TEXTS)})")
    print("="*50)

    embeddings = []
    latencies = []

    # fastembed returns a generator
    start_inf = time.time()
    embeddings_gen = model.embed(SAMPLE_TEXTS)
    for emb in embeddings_gen:
        embeddings.append(emb)
    
    total_time = time.time() - start_inf
    avg_latency = (total_time / len(SAMPLE_TEXTS)) * 1000

    # 1. Latency Check
    print(f"[+] Average Latency: {avg_latency:.2f}ms")
    
    # 2. Similarity Matrix (Internal Consistency)
    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_1_2 = cosine_sim(embeddings[0], embeddings[1])
    sim_1_3 = cosine_sim(embeddings[0], embeddings[2])
    
    print(f"[+] Similarity (ETH Price vs ETH Description): {sim_1_2:.4f} (Expected > 0.7)")
    print(f"[+] Similarity (ETH Price vs Coffee):         {sim_1_3:.4f} (Expected < 0.4)")

    results = {
        "model": MODEL_NAME,
        "avg_latency_ms": avg_latency,
        "consistency_checks": {
            "similar_pair": float(sim_1_2),
            "dissimilar_pair": float(sim_1_3)
        }
    }
    
    with open("data/sovereign_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("\n[RESULT] Benchmark data saved to data/sovereign_benchmark_results.json")
    print(">> Sovereign status: READY FOR DEPLOYMENT." if sim_1_2 > 0.6 else ">> Sovereign status: RE-CALIBRATE.")

if __name__ == "__main__":
    benchmark_sovereign_embeddings()
