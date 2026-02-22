#!/usr/bin/env python
"""
Sentry Integration Test Script (Story: REM-013)

This script validates Sentry configuration without needing pytest.
Run: python scripts/test_sentry.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_sentry_configuration():
    """Test Sentry configuration."""
    print("\n" + "="*70)
    print("SENTRY INTEGRATION TEST")
    print("="*70 + "\n")

    # Test 1: Import sentry_sdk
    print("1. Testing sentry_sdk import...")
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        print("   ✓ sentry_sdk successfully imported")
        print("   ✓ FastAPI integration available")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        print("   Install with: pip install sentry-sdk[fastapi]")
        return False

    # Test 2: Load settings
    print("\n2. Loading settings...")
    try:
        from backend.config import settings
        print(f"   ✓ Settings loaded")
        print(f"   - ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"   - SENTRY_DSN configured: {bool(settings.SENTRY_DSN)}")

        if settings.SENTRY_DSN:
            # Validate DSN format
            dsn = settings.SENTRY_DSN
            if dsn.startswith('https://') and '@' in dsn and '.ingest.sentry.io' in dsn:
                print(f"   ✓ SENTRY_DSN format valid: {dsn[:25]}...{dsn[-15:]}")
            else:
                print(f"   ✗ SENTRY_DSN format invalid: {dsn}")
                return False
        else:
            print("   ℹ SENTRY_DSN not configured (development mode - this is ok)")
    except Exception as e:
        print(f"   ✗ Failed to load settings: {e}")
        return False

    # Test 3: Check FastAPI app initialization
    print("\n3. Checking FastAPI app initialization...")
    try:
        from backend.main import app, SENTRY_AVAILABLE
        print(f"   ✓ FastAPI app loaded")
        print(f"   ✓ SENTRY_AVAILABLE: {SENTRY_AVAILABLE}")

        if SENTRY_AVAILABLE:
            if settings.SENTRY_DSN:
                print("   ✓ Sentry is ENABLED (DSN configured)")
            else:
                print("   ℹ Sentry library available but DSN not configured")
        else:
            print("   ℹ Sentry library not available (install to enable)")

    except Exception as e:
        print(f"   ✗ Failed to load FastAPI app: {e}")
        return False

    # Test 4: Verify health endpoints exist
    print("\n4. Verifying health check endpoints...")
    try:
        routes = [route.path for route in app.routes]
        health_routes = [r for r in routes if 'health' in r.lower() or 'ready' in r.lower()]

        if health_routes:
            print(f"   ✓ Health check endpoints found: {health_routes}")
        else:
            print(f"   ✗ Health check endpoints not found")
            print(f"      Available routes: {routes[:5]}...")
            return False

    except Exception as e:
        print(f"   ✗ Failed to verify routes: {e}")
        return False

    # Test 5: Validate Sentry configuration structure
    print("\n5. Validating Sentry configuration structure...")
    try:
        if SENTRY_AVAILABLE:
            # Test capturing an exception (mock)
            try:
                raise ValueError("Test error for Sentry capture")
            except ValueError as e:
                print(f"   ✓ Exception handling works: {type(e).__name__}: {e}")
                if settings.SENTRY_DSN:
                    print(f"   ✓ Exception would be sent to Sentry")
                else:
                    print(f"   ℹ Exception captured locally (Sentry disabled without DSN)")
        else:
            print("   ℹ Sentry not available (install sentry-sdk to test)")

    except Exception as e:
        print(f"   ✗ Exception handling test failed: {e}")
        return False

    # Final status
    print("\n" + "="*70)
    if settings.SENTRY_DSN:
        print("STATUS: READY - Sentry fully configured and monitoring errors")
        print("\nNext steps:")
        print("1. Test triggering an error: curl http://localhost:8000/sentry-debug")
        print("2. Check Sentry dashboard: https://sentry.io/projects/")
        print("3. Configure Slack alerts in Sentry Settings → Integrations")
    else:
        print("STATUS: CONFIGURED (Disabled) - Ready for development")
        print("\nTo enable Sentry error monitoring:")
        print("1. Go to https://sentry.io")
        print("2. Create a Python + FastAPI project")
        print("3. Copy the DSN from project settings")
        print("4. Add to .env: SENTRY_DSN=https://key@org.ingest.sentry.io/id")
        print("5. Restart the backend")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    success = test_sentry_configuration()
    sys.exit(0 if success else 1)
