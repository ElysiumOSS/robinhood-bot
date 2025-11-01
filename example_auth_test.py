"""
Example script to test Robinhood authentication with enhanced MFA support.

This script demonstrates the new authentication flow with:
- Automatic retry mechanism (3 attempts)
- Timer-based waiting for SMS verification
- Interactive MFA code input
- Support for environment variable MFA codes
"""

from src.core.base_trade_bot import TradeBot
from src.core.config import TradingConfig, StrategyType
from src.utils.logger import logger


def test_authentication():
    """
    Test the authentication flow without executing any trades.
    """
    logger.info("=" * 60)
    logger.info("Starting Robinhood Authentication Test")
    logger.info("=" * 60)
    
    try:
        # Create a minimal valid configuration
        # We use a dummy strategy with weight 1.0 just to pass validation
        # No actual trading will occur during authentication test
        config = TradingConfig(
            enabled_strategies=[StrategyType.SMA_CROSSOVER],
            strategy_weights={StrategyType.SMA_CROSSOVER: 1.0}
        )
        
        logger.info("Initializing TradeBot (this will trigger authentication)...")
        
        # The authentication happens in __init__
        with TradeBot(config=config) as bot:
            logger.info("✓ Authentication successful!")
            logger.info("=" * 60)
            logger.info("Authentication Details:")
            logger.info("  - Connection: Established")
            logger.info("  - Status: Ready for trading")
            logger.info("=" * 60)
            
            # Get account info to verify connection
            try:
                cash_position = bot.get_current_cash_position()
                logger.info(f"Current Cash Position: ${cash_position:.2f}")
            except Exception as e:
                logger.warning(f"Could not retrieve cash position: {e}")
            
            logger.info("=" * 60)
            logger.info("Authentication test completed successfully!")
            logger.info("You can now use the bot for trading operations.")
            logger.info("=" * 60)
            
    except ConnectionError as e:
        logger.error("=" * 60)
        logger.error("Authentication Failed")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error("")
        logger.error("Troubleshooting Steps:")
        logger.error("1. Check your credentials in .env file")
        logger.error("2. Verify your Robinhood account status")
        logger.error("3. Try adding ROBINHOOD_MFA_CODE to .env")
        logger.error("4. Wait 15-30 minutes if rate-limited")
        logger.error("=" * 60)
        raise
    
    except Exception as e:
        logger.error("=" * 60)
        logger.error("Unexpected Error")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    test_authentication()
