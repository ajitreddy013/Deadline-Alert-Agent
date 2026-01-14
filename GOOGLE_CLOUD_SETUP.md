# 🛠️ Google Cloud OAuth Setup Guide

This guide will help you set up the credentials needed to connect multiple Gmail accounts to your Deadline Reminder app.

## Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown (top left) and select **New Project**.
3. Name it `Deadline Reminder Agent` and click **Create**.

## Step 2: Enable the APIs
1. In the sidebar, go to **APIs & Services > Library**.
2. Search for **Gmail API** and click **Enable**.
3. Search for **People API** and click **Enable**. (This is required for the app to see your email address).

## Step 3: Configure the OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in the required info:
   - **App name**: `Deadline Reminder`
   - **User support email**: Your email
   - **Developer contact info**: Your email
4. Click **Save and Continue** to go to the **Scopes** page.
5. Click **Add or Remove Scopes**.
6. At the bottom of the drawer, under **Manually add scopes**, paste this exact URI:
   - `https://www.googleapis.com/auth/gmail.readonly`
7. Click **Add to table**, then scroll down and click **Update**.
8. Scroll to the bottom and click **Save and Continue** to go to **Test Users**.
9. **CRITICAL**: Add the Gmail addresses you want to connect to the **Test Users** list. Google only allows these specific emails to connect until the app is "Verified".
10. Click **Save and Finish**.

## Step 4: Create OAuth Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials** > **OAuth client ID**.
3. Select **Web application** as the Application type.
4. Name it `Deadline Web Client`.
5. Under **Authorized JavaScript origins**, click **+ Add URI** and enter:
   - `http://localhost:8080`
6. Under **Authorized redirect URIs**, click **+ Add URI** and enter **these** (copy exactly):
   - `http://localhost:8080/`
   - `http://localhost:8000/auth/google/callback`
7. Click **Create**.

## Step 5: Update your Backend
1. A window will pop up with your **Client ID** and **Client Secret**.
2. Open your `backend/.env` file and paste them:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```
3. Restart your backend server.

---

## 🔄 Connecting Multiple Accounts
Once the above is set up:
1. Open the app at `http://localhost:8080`.
2. Go to **Settings** (Gear icon ⚙️).
3. Click **Connect New Gmail Account**.
4. Log in with your first account and accept permissions.
5. **Repeat**: Click the button again to log in with a second or third account!

All connected accounts will show up in the "Connected Accounts" list, and the agent will check all of them every 15 minutes for new deadlines.
