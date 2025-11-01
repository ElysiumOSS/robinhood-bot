from src.core.base_trade_bot import TradeBot
from src.core.config import TradingConfig, StrategyType

# 1. Configure the strategies you want to use
my_config = TradingConfig(
    enabled_strategies=[
        StrategyType.SMA_CROSSOVER,
        StrategyType.SENTIMENT,
    ],
    strategy_weights={
        StrategyType.SMA_CROSSOVER: 0.6,
        StrategyType.SENTIMENT: 0.4,
    },
)

# 2. Initialize the TradeBot with your configuration
trade_bot = TradeBot(config=my_config)

# 3. Execute a trade decision for a specific ticker
trade_bot.execute_trade_decision(ticker="INTC")
