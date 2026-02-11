// supabase/functions/sovereign_embed/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.6.0'

// --- DOXO CONFIGURATION ---
// Disable local caching to fit in spartan Edge environments (<500MB RAM)
env.allowLocalModels = false;
env.useBrowserCache = false;

// Pre-warm the model
console.log("[SOVEREIGN] Initializing all-MiniLM-L6-v2...");
const embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
console.log("[SOVEREIGN] Model Ready.");

serve(async (req) => {
    const startTime = Date.now();

    try {
        const { text } = await req.json();

        if (!text) {
            return new Response(
                JSON.stringify({ error: "Missing 'text' field" }),
                { status: 400, headers: { "Content-Type": "application/json" } }
            );
        }

        // Generate Sovereign Embedding
        const output = await embedder(text, {
            pooling: 'mean',
            normalize: true
        });

        const embedding = Array.from(output.data);
        const duration = Date.now() - startTime;

        console.log(`[SOVEREIGN] Embedding generated in ${duration}ms | Length: ${embedding.length}`);

        return new Response(
            JSON.stringify({
                embedding,
                model: 'sovereign-minilm-l6',
                dimensions: 384,
                latency_ms: duration
            }),
            { headers: { "Content-Type": "application/json" } }
        );
    } catch (error) {
        console.error("[SOVEREIGN] CRITICAL_FAILURE:", error);
        return new Response(
            JSON.stringify({ error: error.message }),
            { status: 500, headers: { "Content-Type": "application/json" } }
        );
    }
})
