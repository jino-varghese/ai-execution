# 🔧 Quick Fix for JSON Error

## Problem
Getting this error in the browser?
```
Error analyzing document: unexpected token '<', "<!DOCTYPE..." is not valid JSON
```

## Why This Happens
The Lambda function was returning HTML instead of JSON for POST requests due to missing CORS headers on error responses.

## ✅ Quick Fix (3 Steps)

### Step 1: Update the Lambda Function

Run this command from the project root:

```bash
./update-lambda.sh
```

This will:
- Package the fixed `lambda_function.py`
- Upload it to your Lambda function
- Test that it's working
- Show you the Function URL

**Expected output:**
```
✓ Package created
✓ Function code updated successfully!
✓ Update complete
✓ POST request successful (HTTP 200)
✓ Response is valid JSON
FIX VERIFIED! The JSON error should be resolved.
```

### Step 2: Clear Browser Cache

After updating, **clear your browser cache**:

- **Chrome/Edge:** Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- **Firefox:** Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- **Safari:** Press `Cmd+Option+R`

Or use **Incognito/Private mode** to test.

### Step 3: Test Again

1. Reload your Function URL
2. Click a sample contract (NDA, Service Agreement, Employment)
3. Click "Analyze Document"

✅ **Should work now!**

---

## 🔍 Still Not Working?

### Run the Debug Script

```bash
./debug-lambda.sh
```

This will:
- Check if your function exists
- Test GET and POST requests
- Show what responses you're getting
- Display recent logs
- Tell you exactly what's wrong

### Common Issues

#### Issue 1: Function Not Updated
**Symptom:** Debug script shows HTML in POST response

**Solution:**
```bash
./update-lambda.sh
```

#### Issue 2: Wrong Function Name
**Symptom:** "Function does not exist"

**Solution:**
```bash
# If you used Terraform
cd terraform
./terraform.sh outputs  # Get the function name

# Then update with correct name
./update-lambda.sh YOUR-FUNCTION-NAME us-east-1
```

#### Issue 3: Browser Cache
**Symptom:** Error persists after update

**Solution:**
- Hard refresh: `Ctrl+Shift+R` or `Cmd+Shift+R`
- Use Incognito/Private mode
- Clear all browser data for the site

#### Issue 4: AWS Credentials
**Symptom:** "AWS credentials not configured"

**Solution:**
```bash
aws configure
# Enter your Access Key ID and Secret Access Key
```

---

## 📋 Manual Fix (AWS Console)

If you prefer using the AWS Console:

1. **Go to AWS Lambda Console**
   - https://console.aws.amazon.com/lambda/

2. **Open your function**
   - Find: `legal-document-analyzer` (or your function name)
   - Click to open it

3. **Update the code**
   - Scroll to "Code source"
   - Copy the entire content from `lambda_function.py`
   - Paste it into the editor
   - Click **Deploy** (orange button)

4. **Wait for deployment**
   - Wait 5-10 seconds

5. **Test it**
   - Click the "Test" tab
   - Create a new test event:
     ```json
     {
       "httpMethod": "POST",
       "body": "{\"document\":\"test\",\"type\":\"contract\"}"
     }
     ```
   - Click "Test"
   - Should see JSON response (not HTML)

6. **Try in browser**
   - Clear cache
   - Reload your Function URL
   - Test analysis

---

## 🧪 Verify the Fix

### Quick Test Command

```bash
# Replace with your Function URL
FUNCTION_URL="https://YOUR-FUNCTION-URL.lambda-url.us-east-1.on.aws/"

curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{"document":"This is a test contract","type":"contract"}' \
  | python3 -m json.tool
```

**Should see:** Valid JSON with `risk_score`, `risk_level`, etc.

**Should NOT see:** HTML starting with `<!DOCTYPE`

---

## 🎯 What Was Fixed

### Before (Broken)
```python
# Error responses had no headers
return {
    'statusCode': 500,
    'body': json.dumps({'error': str(e)})  # Missing headers!
}
```

### After (Fixed)
```python
# All responses have proper headers
cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

return {
    'statusCode': 500,
    'headers': cors_headers,  # ✅ Headers included
    'body': json.dumps({'error': str(e)})
}
```

---

## 📚 Additional Resources

### View Logs
```bash
# View recent logs
aws logs tail /aws/lambda/legal-document-analyzer --follow

# Or from Terraform
cd terraform
./terraform.sh logs
```

### Update via Terraform
```bash
cd terraform
./terraform-deploy.sh
```

### Get Function URL
```bash
aws lambda get-function-url-config \
  --function-name legal-document-analyzer \
  --region us-east-1 \
  --query FunctionUrl \
  --output text
```

---

## ✅ Success Checklist

- [ ] Ran `./update-lambda.sh`
- [ ] Saw "FIX VERIFIED" message
- [ ] Cleared browser cache
- [ ] Reloaded Function URL
- [ ] Tested sample contract
- [ ] Analysis works without JSON error

---

## 🆘 Still Need Help?

1. **Run diagnostics:**
   ```bash
   ./debug-lambda.sh > diagnosis.txt
   cat diagnosis.txt
   ```

2. **Check logs:**
   ```bash
   aws logs tail /aws/lambda/legal-document-analyzer --since 5m
   ```

3. **Verify function exists:**
   ```bash
   aws lambda list-functions --region us-east-1 | grep legal
   ```

---

**The fix is in the code repository and ready to deploy!**

Just run `./update-lambda.sh` and clear your browser cache. 🚀
