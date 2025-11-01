"""
Single attempt login - USE ONLY AFTER WAITING 30-60 MINUTES!

This script makes ONE careful attempt to log in after a rate limit cooldown.
"""

import time
from datetime import datetime
import robin_stocks.robinhood as robinhood
from src.utils.credentials import RobinhoodCredentials
from src.utils.logger import logger


def single_careful_attempt():
    """
    Make a single, careful login attempt.
    
    Use this ONLY after:
    - Waiting at least 30-60 minutes
    - Verifying you can log into Robinhood website
    - Checking for any pending account verifications
    """
    credentials = RobinhoodCredentials()
    
    logger.info("=" * 70)
    logger.info("🔐 Robinhood Single Login Attempt")
    logger.info("=" * 70)
    logger.info("Time: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("User: %s", credentials.user)
    logger.info("=" * 70)
    logger.info("")
    logger.info("⚠️  IMPORTANT: Have you waited at least 30-60 minutes?")
    logger.info("⚠️  IMPORTANT: Can you log into Robinhood website?")
    logger.info("")
    
    try:
        response = input("Continue with login attempt? (yes/no): ").strip().lower()
        if response != 'yes':
            logger.info("Cancelled. Good idea to wait longer!")
            return False
    except (EOFError, KeyboardInterrupt):
        logger.info("Cancelled.")
        return False
    
    logger.info("")
    logger.info("Making ONE login attempt...")
    logger.info("Please wait...")
    logger.info("")
    
    time.sleep(2)  # Brief pause
    
    try:
        # Single attempt with SMS
        robinhood.login(
            credentials.user,
            credentials.password,
            expiresIn=86400,
            by_sms=True,
            store_session=True  # Save session to avoid future logins
        )
        
        logger.info("=" * 70)
        logger.info("✅ SUCCESS! Logged in successfully!")
        logger.info("=" * 70)
        logger.info("")
        
        # Verify with account info
        try:
            profile = robinhood.account.build_user_profile()
            cash = float(profile.get('cash', 0))
            logger.info("Account verified:")
            logger.info("  • Cash balance: $%.2f", cash)
            logger.info("  • Username: %s", profile.get('username', 'N/A'))
            logger.info("")
            logger.info("✅ Your account is ready to use!")
            logger.info("The bot will now work normally.")
        except Exception as e:
            logger.warning("Could not fetch profile: %s", e)
        
        logger.info("=" * 70)
        
        # Keep session active
        logger.info("")
        logger.info("📝 Session has been saved to avoid future login issues.")
        logger.info("The bot should stay logged in for 24 hours.")
        logger.info("")
        
        robinhood.logout()
        logger.info("Logged out (but session is saved for next time).")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        
        logger.error("=" * 70)
        logger.error("❌ Login attempt failed")
        logger.error("=" * 70)
        logger.error("Error: %s", error_str)
        logger.error("")
        
        # Analyze the error
        if "'detail'" in error_str or "KeyError" in error_str:
            logger.error("🚫 Still rate-limited or blocked!")
            logger.error("")
            logger.error("This means:")
            logger.error("  • You need to wait longer (try 2-4 hours)")
            logger.error("  • OR your account needs manual verification")
            logger.error("  • OR your IP is temporarily blocked")
            logger.error("")
            logger.error("What to do:")
            logger.error("  1. Log into Robinhood website RIGHT NOW")
            logger.error("  2. Complete ANY pending verifications")
            logger.error("  3. Check your email for security alerts")
            logger.error("  4. Wait at least 2-4 more hours")
            logger.error("  5. If still blocked tomorrow, contact Robinhood support")
            logger.error("")
        elif "challenge" in error_str.lower():
            logger.error("📱 Device approval required")
            logger.error("")
            logger.error("Good news: You're not rate-limited!")
            logger.error("Try running: python approve_login.py")
            logger.error("")
        elif "mfa" in error_str.lower():
            logger.error("🔐 MFA code issue")
            logger.error("")
            logger.error("Check your ROBINHOOD_MFA_CODE in .env file")
            logger.error("Make sure it's the SECRET KEY, not the 6-digit code")
            logger.error("")
        else:
            logger.error("❓ Unexpected error")
            logger.error("")
            logger.error("This might be:")
            logger.error("  • Network issue")
            logger.error("  • Invalid credentials")
            logger.error("  • Robinhood API maintenance")
            logger.error("")
        
        logger.error("=" * 70)
        logger.error("")
        logger.error("⚠️  DO NOT TRY AGAIN FOR AT LEAST 2 HOURS!")
        logger.error("")
        logger.error("Set a timer and wait. Each failed attempt extends the block.")
        logger.error("=" * 70)
        
        return False


def main():
    """Main function."""
    logger.info("")
    logger.info("⏰ Single Attempt Login (Use After Cooldown)")
    logger.info("")
    
    success = single_careful_attempt()
    
    if not success:
        logger.info("")
        logger.info("💤 Recommended: Wait at least 2-4 hours before trying again")
        logger.info("")
        exit(1)
    else:
        logger.info("")
        logger.info("🎉 Success! You can now use the bot normally.")
        logger.info("")
        exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Cancelled by user.")
        exit(0)
