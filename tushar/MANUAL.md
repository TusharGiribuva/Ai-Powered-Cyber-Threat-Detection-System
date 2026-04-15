# Sentinel-X: AI Cyber Threat Detection System
**Final Year Project Setup Manual**

This manual outlines the exact steps required to copy, install, and run this project natively on a new Mac or Windows device for demonstration purposes.

---

## 1. Prerequisites
Before beginning, ensure the new device has **Python 3.8+** installed. 
You can verify this by opening a terminal/command prompt and typing:
```bash
python --version
# or 
python3 --version
```

## 2. Transferring the Project
1. Copy the entire `cyber security threat detection system` folder to the new device (via USB, Google Drive, or GitHub).
2. Open the Terminal (Mac/Linux) or Command Prompt (Windows).
3. Navigate into the project folder:
```bash
# Example for Mac/Linux:
cd "/path/to/cyber security threat detection system"

# Example for Windows:
cd "C:\path\to\cyber security threat detection system"
```

## 3. Installing Dependencies
This project relies on strict library versions defined in `requirements.txt`. Install them using PIP:

**On Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

**On Windows:**
```bash
pip install -r requirements.txt
```
*(Note: It is highly recommended to do this inside a virtual environment `python -m venv venv` if the new device allows it).*

## 4. Running the Dashboard

### Using the Automated Script (Mac / Linux only)
If you are presenting on a Mac or a Linux machine, you can simply use the executable shell script provided:
```bash
chmod +x run.sh
./run.sh
```

### Manual Execution (Windows / Mac / Linux)
If the script does not work, or you are on a Windows machine, you can launch the Streamlit server manually by typing:
```bash
# Make sure you are in the root 'cyber security threat detection system' folder
streamlit run app/main.py
```

## 5. Using the Software During Presentation
Once the command is executed, a local web server will spin up. 
1. Your default web browser should automatically open to `http://localhost:8501`.
2. Expand the left sidebar (click the `>` icon in the top left if it is closed).
3. Toggle the **View Mode** depending on who you are presenting to (Ordinary User vs. Technical Evaluator).
4. Click **Start Monitoring** to begin the live traffic simulation and autonomous AI-blocking demonstration.

## Troubleshooting
- **Port In Use Error:** If Streamlit complains that port 8501 is busy, you can manually assign a new port: `streamlit run app/main.py --server.port 8502`
- **Module Not Found:** Ensure your terminal is in the root directory and that the requirements were successfully installed.
