import sys
sys.path.append("backend/models")
from trade_levels import get_trade_levels

result = get_trade_levels("MSFT", verdict="BULLISH", current_position_entry=403.6)
print(result)
