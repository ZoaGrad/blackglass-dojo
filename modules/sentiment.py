class SentimentMonitor:
    """
    Layer 4: Anti-Drift Sentiment Monitor (The Nervous System).
    Tracks 'Friction' in the environment.
    """
    def __init__(self):
        self.friction_score = 0.0
        self.history = []

    def log_interaction(self, tx_receipt: dict):
        """
        Updates sentiment based on the result of a transaction.
        """
        if tx_receipt['status'] == 'failed':
            self.friction_score += 0.5
        elif tx_receipt['gas_used'] > tx_receipt['gas_limit'] * 0.9:
            self.friction_score += 0.2
        else:
            # Successful, low friction interaction decays the score
            self.friction_score = max(0.0, self.friction_score - 0.1)
            
        self.history.append(self.friction_score)
        
        # Alert check
        if self.friction_score > 5.0:
            print(f">> [SENTINEL] FRICTION ALERT (Score: {self.friction_score}). Environment is Hostile.")
            return "high_friction"
            
        return "nominal"

    def measure_mempool_reaction(self):
        """
        Advanced: Check if we are being front-run.
        (Placeholder for subsequent phase implementation)
        """
        return 0.0
