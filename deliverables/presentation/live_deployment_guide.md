# Live Deployment Guide — Render Docker Web Service

This guide provides step-by-step instructions for deploying the Nasr City Smart Digital Twin system live on Render.

---

## 1. Prerequisites
* A GitHub repository containing the active project code.
* A Render account ([https://render.com](https://render.com)).

---

## 2. Step-by-Step Deployment Instructions

1. **Push Branch to GitHub:**
   Ensure all local changes are committed and pushed to your remote repository branch:
   ```powershell
   git push origin feature/nasr-city-weather-impact-module
   ```

2. **Access Render Dashboard:**
   Log in to your Render Account Dashboard.

3. **Create New Web Service:**
   * Click **New +** in the top right corner and select **Web Service**.
   * Choose **Build and deploy from a Git repository**.

4. **Connect GitHub Repository:**
   Locate and select your `Smart Digital Twin` repository from the connected Git list.

5. **Configure Web Service Parameters:**
   * **Name:** `smart-digital-twin`
   * **Region:** Choose the region closest to you.
   * **Branch:** `feature/nasr-city-weather-impact-module`
   * **Runtime:** Select **Docker**.

6. **Specify Docker Configurations:**
   * **Dockerfile Path:** `Dockerfile.deploy` (Make sure to specify this file instead of the standard `Dockerfile`).

7. **Define Environment Variables:**
   Under the environment sections, add the following key-value pairs:
   * `PYTHONUNBUFFERED` = `1`
   * `ENVIRONMENT` = `production`

8. **Define Health Check Route:**
   Expand the **Advanced** section and configure the health check endpoint:
   * **Health Check Path:** `/api/weather-impact/health`

9. **Deploy:**
   Click **Create Web Service** at the bottom of the page to launch the build.

10. **Monitor Build Progress:**
    Render will parse `Dockerfile.deploy`, download system libraries, install node dependencies, run the frontend build, and start the FastAPI uvicorn daemon.

11. **Retrieve Application URL:**
    Once the build console indicates `Live`, copy the generated `.onrender.com` subdomain URL.

---

## 3. Post-Deployment Verification

Verify deployment integrity by querying the following endpoints:
* **Frontend Access:** `https://<render-service-name>.onrender.com/` (Should render the dashboard welcome page).
* **API Health Check:** `https://<render-service-name>.onrender.com/api/weather-impact/health` (Should return JSON health statuses).
* **Heat Module Status:** `https://<render-service-name>.onrender.com/api/weather-impact/heat/health` (Should return model online statuses).

---

## 4. Staging the Live Link
Once verified, copy the active URL and paste it into [LIVE_APPLICATION_URL.md](file:///C:/Users/mahmo/Documents/Smart%20Digital%20Twin/deliverables/LIVE_APPLICATION_URL.md), replacing the default placeholders.

---

> [!IMPORTANT]
> **Free Tier Cold Starts:** Free Web Services on Render are configured to spin down after 15 minutes of inactivity. When a new request arrives, it triggers a cold start, which can take 1–3 minutes to spin up the container. Make sure to open the link a few minutes before any live presentation.
