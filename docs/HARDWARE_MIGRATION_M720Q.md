# HARDWARE MIGRATION: LENOVO M720Q deployment
## Project: Blackglass Sovereign Infrastructure
**Status: FINAL // OPERATIONAL**

---

## 1. OBJECTIVE
To move the **Sovereign Router** from cloud-based endpoints to local, physical "iron." This eliminates third-party routing vulnerabilities and establishes a true air-gapped compute boundary.

## 2. HARDWARE SPECIFICATIONS
- **Node**: Lenovo M720q Tiny
- **CPU**: Intel Core i5-8500T (6-core)
- **RAM**: 32GB DDR4 (Optimized for local LLM context)
- **Storage**: 500GB NVMe (Primary OS) + 1TB SSD (Sovereign Database)
- **Networking**: Dual NIC (Physical separation of public/private traffic)

## 3. SOFTWARE STACK (THE SOVEREIGN BUILD)
- **Host OS**: Proxmox VE 8.x (for virtualization/snapshots)
- **Container 1 (The Gasket)**: Debian 12 (Minimal) + `blackglass-shard-alpha`
- **Container 2 (The Model)**: Ollama (running Llama 3 / Mistral)
- **Container 3 (The Watchtower)**: `blackglass-variance-core`

## 4. DEPLOYMENT STEPS

### 4.1. OS Hardening
1. Install Proxmox via USB.
2. Disable all non-essential services (NFC, Bluetooth).
3. Implement `ufw` rules to only allow SSH (Key-only) and the Sovereign MCP port.

### 4.2. Local LLM Integration
1. Pull the local model weight: `ollama pull llama3`
2. Update `modules/sovereign_router.py` to target the local endpoint:
   ```python
   LOCAL_ENDPOINT = "http://192.168.1.10:11434/api/generate"
   ```

### 4.3. Sentinel Binding
1. Bind the Sentinel MCP server to the M720q's static IP.
2. Configure `sentinel_status.json` to reside on a shared network drive (NFS/SMB) for cross-system accessibility.

## 5. PHYSICAL SECURITY (THE SOVEREIGN SEAL)
1. **BIOS Lock**: Set Supervisor password.
2. **UEFI Secure Boot**: Enabled.
3. **Physical Tamper**: Place the node in a locked server cabinet.

---

**"If it isn't on local iron, it isn't sovereign."**
