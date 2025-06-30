from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BacktestConfig(BaseModel):
    tradefile: str
    marketfile: str
    sl_pct: float
    target_pct: float
    trail_trigger: Optional[float] = None
    trail_lock: Optional[float] = None
    reentry_count: int = 0
    reentry_mode: Optional[str] = None  # 'RE-IMMEDIATE' or 'RE-DELAYED'
    reentry_delay: Optional[int] = None # candles to wait if delayed
    expiry_mode: Optional[str] = None   # 'weekly' or 'monthly'
    start_time: str = '09:15'
    end_time: str = '15:15'
    # Add more config fields as needed

class BacktestResult(BaseModel):
    summary: Dict[str, Any]
    trade_log: List[Dict[str, Any]]
    equity_curve: List[float] 