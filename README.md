# 🚀 Merge Automator

**Merge Automator** is a Python-based automation tool designed to streamline the process of merging GitLab Merge Requests (MRs) associated with Mantis tickets. It includes Google Sheets integration, encrypted token management, logging, and a minimalist Flask-based web UI for manual control and monitoring.

---

## 📂 Project Structure

```
Merge Automator/
│
├── logs/                         # Log files (daily rotated)
├── templates/                    # Flask frontend templates
├── config.json                   # Configurations for project (execution time, IDs)
├── credentials.json              # Google Sheets API credentials
├── encrypted_tokens.txt          # Encrypted tokens for GitLab & Mantis
├── secret.key                    # Key file for decryption
│
├── app.py                        # Flask application (UI + REST endpoints)
├── merge_automation.py           # Main script to automate merge process
├── config.py                     # Legacy configuration (deprecated)
│
├── mantis_operations.py          # Mantis API operations (get tickets, add notes, etc.)
├── gitlab_operations.py          # GitLab API operations (get MR, merge MR, etc.)
├── google_sheets_operations.py   # Google Sheets API operations (update sheets, etc.)
├── logging_config.py             # Logger configuration (daily rotated logs)
├── config_manager.py             # Reads & writes config.json
├── token_encryptor.py            # Encrypt tokens
├── token_manager.py              # Decrypt tokens for use
├── key_generator.py              # Generates encryption keys
└── utils.py                      # Helper utilities (extract ticket ID, target branch, etc.)
```

---

## ✅ Features

- 🔒 **Secure encrypted tokens** management (Mantis & GitLab).
- ⚙️ **Configurable execution** through a simple JSON file & UI.
- 📝 **Detailed logging** with daily log rotation.
- 📄 **Google Sheets integration** for tracking and status updates.
- 🔹 **Minimal Flask Web UI**:
  - Trigger automation manually.
  - View/download logs.
  - Update runtime configuration.
- 🕟️ **Scheduled runs** configurable through UI.

---

## ⚙️ Prerequisites

- Python 3.8+
- Google Sheets API credentials (`credentials.json`)
- GitLab & Mantis API tokens (encrypted)
- Pip packages:
  ```
  pip install -r requirements.txt
  ```

---

## 📽️ Setup Instructions

### 1. **Clone the repository**
```bash
git clone https://github.com/your-username/merge-automator.git
cd merge-automator
```

### 2. **Create & Encrypt Tokens**
Run the `key_generator.py` to generate a `secret.key`:
```bash
python key_generator.py
```

Encrypt your GitLab and Mantis tokens:
```bash
python token_encryptor.py
```

### 3. **Google Sheets API Setup**
- Obtain `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/).
- Place it in the root directory.

### 4. **Configuration**
Edit the `config.json`:
```json
{
    "EXECUTION_TIME": "22:00",
    "PROMPT_FOR_MERGE": true,
    "REGRESSION_ISSUES_FILTER_ID": 101871,
    "TAG_CODE_REVIEW_AWAITED": 233
}
```

You can later edit these in the **Config UI** exposed on Flask.

---

## 🚀 Running the Automation

### 1. **Manual Run**
```bash
python merge_automation.py
```

### 2. **Run Flask Server (for UI & API)**
```bash
python app.py
```
- Access UI at: [http://localhost:5000](http://localhost:5000)

---

## 🖥️ Flask Web UI Overview

| Feature                  | Description                               |
|--------------------------|-------------------------------------------|
| 🔘 Trigger Merge Job     | Start merging process manually.           |
| 👅 Download Logs         | Git/Mantis/Merge Analytics logs available for download. |
| ⚙️ Edit Configurations   | Modify execution time, flags, filters, etc. |
| 📊 Job Progress          | View job progress in real-time (if enabled). |

---

## 🗓️ Scheduled Job Execution
Set the **execution time** in `config.json` (or via UI):
```json
"EXECUTION_TIME": "22:00"
```
The system will trigger the job at the specified time.

---

## 📜 Logging
Logs are rotated daily and stored in the `logs/` folder.
- `git.log`
- `mantis.log`
- `merge_analytics.log`

They can be downloaded from the Flask UI.

---

## 🔐 Security & Best Practices

- **Do NOT commit `encrypted_tokens.txt` or `secret.key` to GitHub!**
- Add the following to your `.gitignore`:
  ```
  /encrypted_tokens.txt
  /secret.key
  /credentials.json
  /logs/
  ```
- The UI prompts before merges if `PROMPT_FOR_MERGE` is enabled in `config.json`.

---

## 📄 Example Usage

### Trigger Merge from UI
1. Open `http://localhost:5000`
2. Click **Trigger Merge Automation Job**
3. Review logs under **Download Logs**

---

## 🛠️ Tech Stack

- Python 3
- Flask
- Google Sheets API (`gspread`)
- GitLab & Mantis REST APIs
- Cryptography (Fernet)

---

## 🧑‍💻 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a new Pull Request

---

## ⚠️ License

This project is private and proprietary. Do not distribute without permission.

---

## 🙌 Acknowledgements
- [Python Logging Docs](https://docs.python.org/3/library/logging.html)
- [GitLab API Docs](https://docs.gitlab.com/ee/api/)
- [MantisBT API Docs](https://documenter.getpostman.com/view/29959/mantis-bug-tracker-rest-api/7Lt6zkP)
- [Google Sheets API](https://developers.google.com/sheets/api)

---
