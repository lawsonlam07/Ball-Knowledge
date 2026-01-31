from pydantic import BaseModel
from typing import Optional

class TennisEvent(BaseModel):
    event_type: str        # e.g., "power_serve", "backhand_winner", "net_fault"
    player_name: str       # e.g., "Nadal"
    intensity: float       # 0.0 to 1.0
    score_update: Optional[str] = None