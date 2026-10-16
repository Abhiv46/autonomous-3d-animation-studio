from typing import List, Dict, Any, Optional

class AccountManagerAgent:
    """Manages one configured Google Flow account and pauses when its quota is unavailable."""

    def __init__(self, accounts: List[Dict[str, Any]], primary_slot: int = 0):
        self.accounts = {a["slot_index"]: a for a in accounts}
        self.primary_slot = primary_slot

    def select_best_account(self, required_credits: int = 15, current_slot: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Selects only the primary/current account; never fails over to another account."""
        slot = self.primary_slot
        if current_slot is not None:
            try:
                slot = int(str(current_slot).removeprefix("acc_"))
            except ValueError:
                return None
            if slot != self.primary_slot:
                return None
        account = self.accounts.get(slot)
        if (
            account
            and account.get("status") == "ACTIVE"
            and account.get("available_credits", 50) >= required_credits
        ):
            return account
        return None

    def mark_credits_exhausted(self, slot_index: int):
        if slot_index in self.accounts:
            self.accounts[slot_index]["available_credits"] = 0
            self.accounts[slot_index]["status"] = "COOLDOWN"
