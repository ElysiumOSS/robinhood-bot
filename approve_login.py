"""
Interactive login script for Robinhood with device approval support.

Use this script when Robinhood asks you to approve the login on your device.
This script gives you plenty of time to click "Yes, it's me" in the app.
"""

import time
import robin_stocks.robinhood as robinhood
from src.utils.credentials import RobinhoodCredentials
from src.utils.logger import logger


def interactive_login_with_approval():
    """
    Interactive login that waits for device approval.
    """
    credentials = RobinhoodCredentials()
    
    logger.info("=" * 70)
    logger.info("🔐 Robinhood Interactive Login with Device Approval")
    logger.info("=" * 70)
    logger.info("User: %s", credentials.user)
    logger.info("=" * 70)
    
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        logger.info("")
        logger.info("🔄 Login Attempt %d/%d", attempt, max_attempts)
        logger.info("-" * 70)
        
        try:
            # Initial login attempt
            logger.info("Sending login request to Robinhood...")
            time.sleep(1)
            
            robinhood.login(
                credentials.user,
                credentials.password,
                expiresIn=86400,
                by_sms=True
            )
            
            logger.info("=" * 70)
            logger.info("✅ Successfully logged in to Robinhood!")
            logger.info("=" * 70)
            return True
            
        except Exception as e:
            error_str = str(e)
            logger.warning("Initial login failed: %s", error_str)
            
            # Check if it's a challenge/approval required
            if "challenge" in error_str.lower() or "403" in error_str or "'detail'" in error_str:
                logger.info("")
                logger.info("=" * 70)
                logger.info("⚠️  DEVICE APPROVAL REQUIRED")
                logger.info("=" * 70)
                logger.info("Robinhood is asking you to verify this login.")
                logger.info("")
                logger.info("📱 PLEASE DO THE FOLLOWING NOW:")
                logger.info("   1. Open your Robinhood mobile app")
                logger.info("   2. Look for a notification or prompt")
                logger.info("   3. Tap 'Yes, it's me' or 'Approve'")
                logger.info("   4. Wait for the confirmation message")
                logger.info("=" * 70)
                logger.info("")
                
                # Give extended time for approval
                total_wait = 180  # 3 minutes
                chunk_size = 30  # Update every 30 seconds
                
                for elapsed in range(0, total_wait, chunk_size):
                    remaining = total_wait - elapsed
                    logger.info("⏳ Waiting for approval... (%d seconds remaining)", remaining)
                    logger.info("   👉 Click 'Yes, it's me' in your Robinhood app NOW!")
                    time.sleep(chunk_size)
                
                logger.info("")
                logger.info("Checking if login was approved...")
                time.sleep(2)
                
                # Try to verify the approval
                try:
                    robinhood.login(
                        credentials.user,
                        credentials.password,
                        expiresIn=86400,
                        by_sms=True
                    )
                    
                    logger.info("=" * 70)
                    logger.info("✅ Login approved and verified successfully!")
                    logger.info("=" * 70)
                    return True
                    
                except Exception as verify_error:
                    logger.error("Verification after approval failed: %s", verify_error)
                    
                    if attempt < max_attempts:
                        wait_time = 20 * attempt
                        logger.info("")
                        logger.info("Waiting %d seconds before retry...", wait_time)
                        time.sleep(wait_time)
                    else:
                        logger.error("")
                        logger.error("=" * 70)
                        logger.error("❌ All login attempts failed")
                        logger.error("=" * 70)
                        logger.error("Possible issues:")
                        logger.error("  • You didn't approve the login in time")
                        logger.error("  • Account requires additional verification")
                        logger.error("  • IP address may be temporarily blocked")
                        logger.error("  • Incorrect credentials")
                        logger.error("")
                        logger.error("What to do:")
                        logger.error("  1. Log into Robinhood app/website directly")
                        logger.error("  2. Complete any pending security verifications")
                        logger.error("  3. Wait 15-30 minutes and try again")
                        logger.error("  4. Check your credentials in .env file")
                        logger.error("=" * 70)
                        return False
            else:
                logger.error("Unexpected error: %s", e)
                if attempt < max_attempts:
                    logger.info("Retrying in 10 seconds...")
                    time.sleep(10)
    
    return False


def main():
    """Main function."""
    logger.info("")
    logger.info("This script will help you log into Robinhood when device approval is needed.")
    logger.info("")
    
    try:
        success = interactive_login_with_approval()
        
        if success:
            logger.info("")
            logger.info("🎉 You're now logged in!")
            logger.info("You can now run your trading bot.")
            
            # Test the connection
            try:
                profile = robinhood.account.build_user_profile()
                logger.info("")
                logger.info("Account verified:")
                logger.info("  • Cash: $%.2f", float(profile.get('cash', 0)))
                logger.info("  • User: %s", profile.get('username', 'N/A'))
            except Exception as profile_error:
                logger.warning("Could not fetch profile: %s", profile_error)
            
            # Logout
            logger.info("")
            logger.info("Logging out...")
            robinhood.logout()
            logger.info("✓ Logged out successfully")
        else:
            logger.error("")
            logger.error("❌ Login failed. Please check the errors above.")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⚠️  Cancelled by user")
        exit(0)
    except Exception as e:
        logger.error("")
        logger.error("Fatal error: %s", e)
        exit(1)


if __name__ == "__main__":
    main()
