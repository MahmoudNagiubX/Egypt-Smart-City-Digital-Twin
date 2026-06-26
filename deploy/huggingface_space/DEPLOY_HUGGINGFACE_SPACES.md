# Hugging Face Spaces Deployment Guide

This guide provides step-by-step instructions for deploying the Smart Digital Twin system to Hugging Face Spaces using the Docker SDK.

---

## 1. Step-by-Step Deployment Instructions

1. **Create a Hugging Face Account:**
   Go to [https://huggingface.co](https://huggingface.co) and sign up if you do not have an account.

2. **Create a New Space:**
   * Click on your profile icon in the top right corner and select **New Space**.
   * **Space Name:** `smart-digital-twin`
   * **License:** Select `mit` or leave as default.
   * **SDK:** Select **Docker**.
   * **Docker Template:** Select **Blank** (or standard docker container).
   * **Hardware:** Select **CPU Basic** (Free).
   * **Visibility:** **Public**.

3. **Create the Space:**
   Click **Create Space** at the bottom of the page.

4. **Clone the Space Repository Locally:**
   On the new Space page, copy the Git clone command and run it in a separate folder on your local machine:
   ```bash
   git clone https://huggingface.co/spaces/<your-username>/smart-digital-twin
   ```

5. **Generate the Clean Build Package:**
   Open a PowerShell terminal in the main project directory (`C:\Users\mahmo\Documents\Smart Digital Twin`) and run:
   ```powershell
   .\deploy\huggingface_space\prepare_space_copy.ps1
   ```
   This generates a clean build directory at `deploy/huggingface_space_build/`.

6. **Copy Build Contents to the Cloned Space Repo:**
   Copy all files and folders inside `deploy/huggingface_space_build/` and paste them into the root of your cloned Hugging Face Space repository.

7. **Commit and Push to Hugging Face:**
   In your cloned Space repository terminal, run:
   ```bash
   git add .
   git commit -m "hf deploy: initial import of smart digital twin application"
   git push
   ```
   *Note: If pushing files larger than 10MB fails, verify if Hugging Face LFS is required or prompt authentication.*

8. **Monitor the Build:**
   Go to your Hugging Face Space page in your browser. It will automatically detect the changes, build the multi-stage Docker image, and run the container on port 7860.

9. **Retrieve the Live URL:**
   Once the status changes to `Running`, test the following endpoints in your browser:
   * Main App: `https://huggingface.co/spaces/<your-username>/smart-digital-twin`
   * API Health Check: `https://huggingface.co/spaces/<your-username>/smart-digital-twin/api/weather-impact/health`
   * Heat Health Status: `https://huggingface.co/spaces/<your-username>/smart-digital-twin/api/weather-impact/heat/health`

10. **Record the Final Link:**
    Add the live URL to your [LIVE_APPLICATION_URL.md](file:///C:/Users/mahmo/Documents/Smart%20Digital%20Twin/deliverables/LIVE_APPLICATION_URL.md) file.

---

## 2. Troubleshooting Guide

### Port Binding Errors
* **Symptom:** Space logs indicate connection refused or failed port checks.
* **Resolution:** Ensure the Uvicorn command in the Dockerfile is running on port `7860` (`--port 7860`) and matches the `app_port: 7860` config in the metadata `README.md`.

### Frontend Loads but API Calls Fail
* **Symptom:** UI displays loading stutters or console logs print `404` or `Connection Refused` on API paths.
* **Resolution:** Verify that `frontend/src/api/client.ts` defaults to same-origin relative URLs (`|| ""`) instead of hardcoded `127.0.0.1:8000` URLs.

### Path Resolution Failures
* **Symptom:** Container crashes immediately during startup, indicating missing files under `/app/frontend/dist/` or `backend/app/data/`.
* **Resolution:** Ensure the multi-stage Docker copy paths match the workspace layout, and `PYTHONPATH` is explicitly set to `/app`.

### Write Permission Denied
* **Symptom:** Backend prints `PermissionError` when trying to save weather forecast or route cached JSONs.
* **Resolution:** Hugging Face runs containers as non-root user `1000`. Confirm the Dockerfile contains `RUN chmod -R 777 /app/backend/app/data/nasr_city` to allow dynamic outputs write access.
