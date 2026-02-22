# Sentry Error Monitoring - Setup Guide

**Story:** STORY-REM-013 - Integrate Sentry Error Monitoring
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Priority:** CRITICAL
**Date Created:** 2026-02-23

---

## Overview

Sentry is an error tracking and performance monitoring platform that captures exceptions, logs, and performance traces from your application. This guide covers setup and testing of Sentry integration for the Consulta Processual API.

## Current Status

✅ **Already Implemented:**
- sentry_sdk imported in backend/main.py (lines 27-33)
- Conditional initialization with FastApiIntegration (lines 47-55)
- SENTRY_DSN setting in backend/config.py (line 41)
- Traces enabled (traces_sample_rate=0.1)
- Environment variable configuration

❌ **Still Required:**
- Create Sentry project at sentry.io
- Obtain DSN (Data Source Name)
- Configure SENTRY_DSN environment variable
- Test integration with error triggering
- Configure Slack alerts (optional)

---

## Step 1: Create Sentry Account & Project

### 1.1 Sign Up / Log In
1. Go to https://sentry.io
2. Click "Sign Up" or log in with existing account
3. Verify email if new account

### 1.2 Create New Project
1. Click "Projects" in sidebar
2. Click "Create Project" button
3. Select **Python** as platform
4. Select **FastAPI** as framework (or generic Python)
5. Project name: `consulta-processo` (or preferred name)
6. Alert frequency: "Every new issue" or "Alert me on every new event"
7. Click "Create Project"

### 1.3 Get DSN (Data Source Name)
1. After project creation, you'll see project setup page
2. Look for "DSN" field showing format: `https://xxxxx@xxxxx.ingest.sentry.io/12345`
3. **Copy the full DSN** - you'll need this next

---

## Step 2: Configure Sentry DSN

### 2.1 Add to .env File
Create or update `.env` file in project root:

```bash
# Sentry Error Monitoring
SENTRY_DSN=https://your_key@your_org.ingest.sentry.io/your_project_id
```

### 2.2 Verify Configuration
The backend/main.py will load SENTRY_DSN from:
1. .env file (via python-dotenv)
2. Environment variable (if .env not found)
3. Default: "" (disabled)

Check if loaded correctly:
```bash
# Backend should log on startup:
# "Sentry initialized for environment: development"
```

---

## Step 3: Test Sentry Integration

### 3.1 Manual Test - Trigger Error
Access the debug endpoint to manually trigger an error:

```bash
# This endpoint deliberately crashes
curl http://localhost:8000/sentry-debug

# Expected response: 500 Internal Server Error
```

The error should appear in Sentry dashboard within 1-2 seconds.

### 3.2 Verify in Sentry Dashboard
1. Go to https://sentry.io/projects/
2. Click your project
3. Click "Issues" tab
4. You should see the triggered error listed

### 3.3 Example Error in Sentry
```
ZeroDivisionError: division by zero
  File: backend/main.py
  Line: xxx in trigger_error
  Error: 1 / 0
```

### 3.4 Test with Real API Errors
Test with actual process search failures:

```bash
# Invalid process number - should trigger DataJudAPIException
curl -X POST http://localhost:8000/processes/1 \
  -H "Content-Type: application/json"

# This will be captured by Sentry if SENTRY_DSN is configured
```

---

## Step 4: Configure Slack Alerts (Optional)

### 4.1 Connect Slack Workspace
1. In Sentry, go to Settings → Integrations
2. Search for "Slack"
3. Click "Install" button
4. Authorize Sentry in your Slack workspace

### 4.2 Create Alert Rule
1. Go to Alerts → Alert Rules
2. Click "Create Alert Rule"
3. Configure:
   - **Condition:** When `event.level` is `error` or `fatal`
   - **Action:** Send Slack notification to #alerts channel
   - **Frequency:** On every new issue

### 4.3 Test Slack Alert
1. Trigger error again (curl /sentry-debug)
2. Check Slack channel - should get notification within 30 seconds

---

## Step 5: Configure Environment-Specific Settings

### Development
```bash
SENTRY_DSN=https://dev_key@dev.ingest.sentry.io/dev_id
ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1  # Trace 10% of requests
```

### Staging
```bash
SENTRY_DSN=https://staging_key@staging.ingest.sentry.io/staging_id
ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.5  # Trace 50% of requests
```

### Production
```bash
SENTRY_DSN=https://prod_key@prod.ingest.sentry.io/prod_id
ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Trace 10% of requests (reduce for performance)
```

---

## Step 6: Monitor Performance Traces

### 6.1 View Transaction Traces
1. In Sentry, go to "Performance" tab
2. You'll see traces from your API endpoints
3. Click on a transaction to see waterfall view

### 6.2 Slow Transaction Example
```
POST /processes/bulk (0.542s)
├─ DataJud API calls (0.500s) - 50 concurrent
├─ Database save (0.020s)
└─ Response serialization (0.022s)
```

### 6.3 Set Performance Thresholds
1. Alerts → Create Alert Rule
2. Condition: "Throughput" or "Transaction Duration"
3. Alert if any transaction > 1000ms (1 second)

---

## Step 7: User Context & Breadcrumbs

### 7.1 Adding User Context
When users are authenticated, add context:

```python
# In route handler
if user:
    sentry_sdk.set_user({
        "id": user.id,
        "email": user.email,
        "username": user.username
    })
```

### 7.2 Adding Breadcrumbs
Breadcrumbs are tracked events leading to an error:

```python
# Before error might occur
import sentry_sdk

sentry_sdk.capture_breadcrumb(
    message="Bulk search started",
    level="info",
    data={"count": 50}
)

# If error occurs later, breadcrumb shows context
```

---

## Troubleshooting

### Issue: Sentry Not Capturing Errors
**Solution:**
1. Check SENTRY_DSN is set correctly (full DSN from Step 1.3)
2. Verify sentry_sdk is installed: `pip list | grep sentry`
3. Check FastAPI integration loaded: look for "Sentry initialized" log
4. Test endpoint should crash: curl http://localhost:8000/sentry-debug

### Issue: DSN Not Loading
**Solution:**
1. Verify .env file exists in project root
2. Check SENTRY_DSN line has no spaces: `SENTRY_DSN=https://...` (no spaces)
3. Reload FastAPI app after changing .env
4. Check environment variables: `echo $SENTRY_DSN`

### Issue: Slack Alerts Not Working
**Solution:**
1. Verify Slack integration authorized in Sentry Settings
2. Check alert rule destination is correct channel
3. Verify Sentry app has permission in Slack
4. Test: Trigger error manually, check Slack within 30s

### Issue: No Performance Data
**Solution:**
1. Verify traces_sample_rate > 0 (default: 0.1)
2. Make API requests to generate traces
3. Wait 1-2 minutes for data to appear
4. Check if requests are fast (traces filter by duration)

---

## Performance Considerations

### Tracing Overhead
- `traces_sample_rate=0.1` means 10% of requests are fully traced
- This is good balance: not too many, but enough data for analysis
- For high-traffic production, reduce to 0.01-0.05

### Sample Configuration by Environment
| Environment | traces_sample_rate | reason |
| ----------- | ------------------ | ------ |
| development | 0.5 | Want detailed data while developing |
| staging | 0.3 | Good balance for testing |
| production | 0.1 | Avoid performance impact on users |

---

## Best Practices

1. **Ignore Noisy Errors**
   - Settings → Filters → Ignore errors from known 3rd parties

2. **Group Similar Issues**
   - Settings → Issue Grouping → Configure fingerprints
   - Prevents duplicate error reports

3. **Release Tracking**
   - Set release version when deploying
   - Helps correlate errors with code versions

4. **Custom Context**
   - Always add user/request context for debugging
   - Breadcrumbs show what happened before error

5. **Error Budgeting**
   - Monitor error rate trends
   - Set up alerts for error spikes

---

## Testing Checklist

- [ ] Sentry account created at sentry.io
- [ ] Project created (Platform: Python, Framework: FastAPI)
- [ ] DSN copied from project settings
- [ ] SENTRY_DSN added to .env file
- [ ] Backend restarted (logs show "Sentry initialized")
- [ ] curl /sentry-debug triggers error
- [ ] Error appears in Sentry dashboard within 2 seconds
- [ ] Multiple errors can be grouped and searched
- [ ] Performance traces visible (Performance tab)
- [ ] Slack integration configured (optional)
- [ ] Slack alert tested (optional)

---

## Next Steps

1. **For Development:** Configure dev project, enable debug endpoint
2. **For Staging:** Create separate staging project, monitor traces
3. **For Production:** Create prod project with lower sample rate, set alerts

---

## References

- Sentry Docs: https://docs.sentry.io/product/
- FastAPI Integration: https://docs.sentry.io/platforms/python/integrations/fastapi/
- Python SDK: https://docs.sentry.io/platforms/python/
- Slack Integration: https://docs.sentry.io/product/integrations/slack/

---

**Story:** STORY-REM-013
**Status:** Ready for Testing (requires DSN from Sentry.io)
**Last Updated:** 2026-02-23
