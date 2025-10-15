# Streamlit Cloud Setup Guide

## Prerequisites
- XAI API Key (from x.ai)
- GitHub repository with your code

## Step 1: Configure Secrets in Streamlit Cloud

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io/
2. Click on your deployed app
3. Click on "⚙️ Settings" in the bottom right
4. Go to the "Secrets" tab
5. Add your API key in TOML format:

```toml
XAI_API_KEY = "your-xai-api-key-here"
```

6. Click "Save"

## Step 2: Verify Environment Variables

The app reads configuration from `config.py` which loads from environment variables:

```python
XAI_API_KEY = os.getenv("XAI_API_KEY")
```

Streamlit Cloud automatically loads secrets as environment variables.

## Step 3: Restart Your App

After adding secrets:
1. Click "Reboot app" from the menu
2. Wait for the app to restart
3. Try logging in again

## Step 4: Test the Setup

1. Navigate to your app URL
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`
3. If configured correctly, you should see the main interface
4. Try asking a question to verify the AI is working

## Troubleshooting

### Error: "XAI_API_KEY is not set"

**Solution:**
- Double-check the secret name matches exactly: `XAI_API_KEY`
- Ensure there are no extra spaces or quotes around the key
- Reboot the app after adding secrets

### Error: "Failed to initialize OpenAI client"

**Solution:**
- Verify your XAI API key is valid
- Check if you have credits/quota remaining on x.ai
- Try generating a new API key from x.ai dashboard

### App Crashes on Login

**Solution:**
1. Check the logs in Streamlit Cloud (click "Manage app" → "Logs")
2. Look for the specific error message
3. Verify all dependencies are installed (check `requirements.txt`)

## Getting Your XAI API Key

1. Go to https://x.ai/
2. Sign up or log in
3. Navigate to API settings
4. Create a new API key
5. Copy the key and add it to Streamlit Cloud secrets

## Alternative: Local Development

For local development, create a `.env` file in your project root:

```env
XAI_API_KEY=your-xai-api-key-here
OPENAI_API_KEY=your-openai-key-if-needed
```

The app will automatically load these using `python-dotenv`.

## Security Best Practices

1. ✅ **Never commit API keys** to your repository
2. ✅ **Use Streamlit Secrets** for cloud deployment
3. ✅ **Use .env files** (gitignored) for local development
4. ✅ **Rotate API keys** periodically
5. ✅ **Monitor API usage** to detect unusual activity

## Requirements File

Ensure your `requirements.txt` includes:

```txt
streamlit
openai
chromadb
sentence-transformers
PyPDF2
python-dotenv
```

## Support

If you continue to experience issues:
1. Check Streamlit Cloud status
2. Review the app logs for detailed error messages
3. Verify your XAI account has active credits
4. Test the API key using a simple curl command:

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "grok-4-0709",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```
