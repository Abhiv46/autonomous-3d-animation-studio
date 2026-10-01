from typing import List, Dict, Any, Optional

class AccountManagerAgent:
    """Intelligently orchestrates up to 8 Google Flow accounts. Manages credit tracking, cooldowns, and seamless job handoffs without restarting completed work."""

    def __init__(self, accounts: List[Dict[str, Any]]):
        self.accounts = {a["slot_index"]: a for a in accounts}

    def select_best_account(self, required_credits: int = 15, current_slot: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Prefers keeping the entire story on the current account if sufficient credits exist; otherwise switches to next healthy account."""
        # 1. Check current slot first to avoid unnecessary story splitting
        if current_slot is not None and current_slot in self.accounts:
            curr = self.accounts[current_slot]
            if curr.get("status") == "ACTIVE" and curr.get("available_credits", 50) >= required_credits:
                return curr

        # 2. Find next active account with available credits
        for slot in sorted(self.accounts.keys()):
            acc = self.accounts[slot]
            if acc.get("status") == "ACTIVE" and acc.get("available_credits", 50) >= required_credits:
                return acc

        return None

    def mark_credits_exhausted(self, slot_index: int):
        if slot_index in self.accounts:
            self.accounts[slot_index]["available_credits"] = 0
            self.accounts[slot_index]["status"] = "COOLDOWN"
