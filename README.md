# Pterodactyl Auto Backup Tool

This tool automatically backs up all applicable servers on a Pterodactyl panel.  
It also includes a **dry run mode**, where the tool shows the actions it *would* perform but does not actually execute them.

---

## ⚠️ Warning: API Key Security

API keys give access to critical functions of your Pterodactyl panel. Please follow these security guidelines:

- **Do not share your API keys** publicly or commit them to version control
- **Restrict permissions** on your keys to only what's needed
- **Rotate keys regularly** and delete unused ones.

Failure to secure your keys could lead to unauthorized access to your servers.

---

## Setup

Setting up this tool is simple. Just complete the configuration as described in the detailed instructions below:

![Panel Overview](https://github.com/user-attachments/assets/bf6e8221-d32b-4e41-98e2-9596a4cbb353)

### 1. Get Your Panel URL

Open your panel in a web browser and copy the URL. Paste it into the `PANEL_URL` field in the configuration.

---

### 2. Generate an Admin API Key

To do this:

- Go to the **Admin** section of your panel.
- Navigate to the **Application API** tab.
- Create a new API key:
  - Allow **read** access for servers.
  - Add a description (e.g., *Backup Tool*).
  - Click **Create Credentials**.
- Copy the new key and add it to the `ADMIN_API_KEY` field in the configuration.

![Admin API Step 1](https://github.com/user-attachments/assets/322fec42-ab86-4e95-8145-d4349396f4f6)  
![Admin API Step 2](https://github.com/user-attachments/assets/17ada8c6-fe7c-44df-8814-4fc198a62054)

---

### 3. Generate a User API Key

To do this:

- Go to your **Account Settings**.
- Navigate to the **API Credentials** tab.
- Add a description and click **Create**.
- Copy the generated key and paste it into the `CLIENT_API_KEY` field in the configuration.

![User API Key](https://github.com/user-attachments/assets/1bcbf7f2-9224-4ec8-afeb-1804a09ab254)

---

### 4. Done!

The tool is now set up. Simply run the script to begin using it.
