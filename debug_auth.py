"""
Debug script to inspect what Robinhood API is actually returning.

This will help us understand why authentication is failing.
"""

import requests
import json
from src.utils.credentials import RobinhoodCredentials
from src.utils.logger import logger


def debug_robinhood_response():
    """
    Make a raw API call to see what Robinhood is actually returning.
    """
    credentials = RobinhoodCredentials()
    
    url = "https://api.robinhood.com/oauth2/token/"
    
    payload = {
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'expires_in': 86400,
        'grant_type': 'password',
        'password': credentials.password,
        'scope': 'internal',
        'username': credentials.user,
        'challenge_type': 'sms',
        'device_token': '1234567890abcdef'
    }
    
    logger.info("=" * 70)
    logger.info("🔍 Debugging Robinhood API Response")
    logger.info("=" * 70)
    logger.info("User: %s", credentials.user)
    logger.info("URL: %s", url)
    logger.info("=" * 70)
    
    try:
        response = requests.post(url, json=payload)
        
        logger.info("Status Code: %d", response.status_code)
        logger.info("Headers: %s", dict(response.headers))
        logger.info("=" * 70)
        
        # Try to parse as JSON
        try:
            data = response.json()
            logger.info("Response Body (JSON):")
            logger.info(json.dumps(data, indent=2))
        except ValueError:
            logger.info("Response Body (Raw Text):")
            logger.info(response.text)
        
        logger.info("=" * 70)
        
        # Check what's in the response
        if response.status_code == 403:
            logger.warning("⚠️  403 Forbidden - This usually means:")
            logger.warning("  • Account verification/approval required")
            logger.warning("  • Too many failed login attempts (rate limited)")
            logger.warning("  • Invalid credentials")
            logger.warning("  • IP address blocked")
            
        if response.status_code == 200:
            logger.info("✅ Authentication would succeed!")
            data = response.json()
            if 'challenge' in data:
                logger.info("📱 Challenge required:")
                logger.info("  Type: %s", data['challenge'].get('type'))
                logger.info("  ID: %s", data['challenge'].get('id'))
                logger.info("  Remaining attempts: %s", data['challenge'].get('remaining_attempts'))
            elif 'mfa_required' in data:
                logger.info("🔐 MFA required:")
                mfa_type_val = data.get('mfa_type')
                if isinstance(mfa_type_val, str) and mfa_type_val.lower() in {"sms", "totp", "app", "email"}:
                    logger.info("  MFA type: %s", mfa_type_val)
                else:
                    logger.info("  MFA type: [redacted or unknown]")
            elif 'access_token' in data:
                logger.info("✅ Access token received - login successful!")
        
        logger.info("=" * 70)
        logger.info("")
        logger.info("💡 Analysis:")
        
        if response.status_code == 403:
            try:
                data = response.json()
                if 'detail' in data:
                    logger.info("  Error detail: %s", data['detail'])
                else:
                    logger.warning("  ⚠️  No 'detail' key in response!")
                    logger.info("  Available keys: %s", list(data.keys()))
                    logger.info("")
                    logger.info("  This is why robin_stocks is crashing with KeyError!")
                    logger.info("  The API is returning a 403 but without the expected format.")
                    logger.info("")
                    logger.info("  Possible reasons:")
                    logger.info("    1. You've been rate-limited (too many attempts)")
                    logger.info("    2. Your IP has been temporarily blocked")
                    logger.info("    3. Robinhood has flagged your account for review")
                    logger.info("    4. You need to verify your account on the website first")
            except ValueError:
                logger.warning("  Response is not valid JSON!")
                logger.info("  Raw response: %s", response.text[:500])
        
        logger.info("=" * 70)
        
        # Recommendations
        logger.info("")
        logger.info("📋 Recommendations:")
        logger.info("")
        
        if response.status_code == 403:
            logger.info("  1. WAIT 30-60 minutes before trying again")
            logger.info("     (You may be rate-limited from too many attempts)")
            logger.info("")
            logger.info("  2. Log into Robinhood website/app directly")
            logger.info("     URL: https://robinhood.com/login")
            logger.info("     Complete any pending verifications")
            logger.info("")
            logger.info("  3. Check your email for security alerts")
            logger.info("     Robinhood may have sent you a warning")
            logger.info("")
            logger.info("  4. Try from a different network/IP")
            logger.info("     Your current IP might be blocked")
            logger.info("")
            logger.info("  5. Contact Robinhood support if issue persists")
            logger.info("     They may have locked your API access")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error("Error making request: %s", e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_robinhood_response()
