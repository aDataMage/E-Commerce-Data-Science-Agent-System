---
description: How to deploy the AGDSW app to Streamlit Cloud securely
---

# Deploying to Streamlit Cloud

This guide explains how to deploy your app to Streamlit Cloud without exposing your `.env` file or secrets on GitHub.

## 1. Prepare your Repository
Ensure your project is ready for deployment:

1.  **Check `.gitignore`**: Verify that `.env` is listed in your `.gitignore` file.
    *   *Status*: **Checked**. Your `.gitignore` already includes `.env`.
2.  **Check Database**: Ensure `ecommerce.db` is **NOT** ignored so it gets uploaded.
    *   *Status*: **Fixed**. I have commented it out in `.gitignore` for you.
3.  **requirements.txt**: Ensure all dependencies are listed.
    *   *Status*: **Checked**. Your `requirements.txt` looks ready.
4.  **Push to GitHub**: Commit and push your code (including `ecommerce.db`) to your GitHub repository.
    *   *Note*: Since `.env` is ignored, it will NOT be pushed. This is correct.

## 2. Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your GitHub repository, branch (usually `main`), and the main file path (`app.py`).
4.  Click **"Deploy"**.

## 3. Configure Secrets (Crucial Step)
Since your `.env` file is not on GitHub, your app will fail to start initially (or fail when you try to run it) because it cannot find `GEMINI_API_KEY`. You need to add it manually in the Streamlit Cloud dashboard.

1.  On your app's dashboard in Streamlit Cloud, click the **Settings** menu (three dots usually in the bottom right or top right).
2.  Select **"Settings"**.
3.  Go to the **"Secrets"** tab.
4.  Paste your secrets in TOML format suitable for Streamlit.
    *   Streamlit secrets are essentially environment variables.
    *   For your `.env` content, you would format it like this:

    ```toml
    GEMINI_API_KEY = "your-actual-api-key-here"
    ```

5.  Click **"Save"**.

## 4. How Code Accesses Secrets
Your code uses `os.getenv("GEMINI_API_KEY")`.
-   Streamlit Cloud automatically loads variables defined in "Secrets" into the environment so `os.getenv` works as expected.
-   You do **not** need to change your code.

## Troubleshooting
-   **"Module not found"**: Check if the missing package is in `requirements.txt`.
-   **"Key Error"**: Double-check the variable name in the Secrets tab matches `GEMINI_API_KEY`.
