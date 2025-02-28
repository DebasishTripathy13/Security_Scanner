# Security Scanner Dashboard

A powerful and comprehensive security scanning tool that automates vulnerability assessments using multiple security tools, enhanced with AI-powered analysis.

## Overview
The Security Scanner Dashboard provides an integrated platform for executing various security scanning tools against designated targets. It streamlines result collection, organization, and AI-driven analysis to enhance security assessments. **This tool is strictly for authorized security testing only.**

## Features
- **Multi-Tool Integration**: Combines Nmap, Gobuster, FFUF, and SQLMap in a single platform.
- **Web Interface**: User-friendly Streamlit dashboard for scan configuration and result visualization.
- **Command Line Support**: Enables scans to be executed directly from the terminal.
- **AI-Powered Analysis**: Uses Google's Gemini API to interpret scan results and provide security recommendations.
- **Comprehensive Reporting**: Generates detailed reports in JSON format.
- **Scope Control**: Ensures only authorized targets are scanned.
- **Customizable Scan Types**: Offers Basic, Full, and Custom scan options.
- **Real-time Progress Tracking**: Monitors ongoing scans with live updates.
- **Easy Export**: Download reports in JSON format for further analysis.
- **Diagnostic Tool**: Detects common setup and configuration issues.

## Prerequisites
- Python 3.8 or higher
- Required security tools:
  - **Nmap**: Port scanning and service detection
  - **Gobuster**: Directory enumeration
  - **FFUF**: Web fuzzing and endpoint discovery
  - **SQLMap**: SQL injection testing

## Installation
### Standard Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/debasishtripathy13/security_scanner.git
   cd security-scanner
   ```
2. Set up a Python virtual environment (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   python -m pip install -r requirements.txt
   ```
4. Run the setup script:
   ```sh
   python setup.py
   ```
5. Configure environment settings:
   ```sh
   cp .env.example .env
   ```
   Edit `.env` with:
   - Gemini API key
   - Authorized target domains and IP ranges
   - Other necessary settings

### Docker Installation (Alternative)
1. Build the Docker image:
   ```sh
   docker build -t security_scanner .
   ```
2. Run the container:
   ```sh
   docker run -p 8501:8501 -v $(pwd)/reports:/app/reports -e GEMINI_API_KEY=<your_gemini_api_key> security-scanner
   ```
   *(Replace `<your_gemini_api_key>` with your actual Gemini API key.)*

## External Tool Installation
If setup reports missing tools, install them as follows:

### Linux (Debian/Ubuntu)
```sh
sudo apt update
sudo apt install nmap gobuster sqlmap
go install github.com/ffuf/ffuf@latest
```
Ensure `$PATH` includes Go binaries (`$HOME/go/bin` or `/root/go/bin`).

### macOS
```sh
brew install nmap gobuster ffuf sqlmap
```

### Windows (Using Chocolatey & Go)
```sh
choco install nmap sqlmap
go install github.com/OJ/gobuster/v3@latest
go install github.com/ffuf/ffuf@latest
```
Ensure Go is installed and binaries are in the system path.

## Configuration
Modify `.env` file:
```ini
# Security Scanner Configuration
TARGET_DOMAINS=google.com,example.com
TARGET_IPS=192.168.0.0/24,10.0.0.0/24
MAX_RETRIES=3
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage
### Web Interface
1. Start the Streamlit app:
   ```sh
   streamlit run app.py
   ```
2. Open [http://localhost:8501](http://localhost:8501).
3. Select scan parameters:
   - Choose target type: **Domain** or **IP Address**
   - Enter the target (must be authorized)
   - Select scan type: **Basic, Full, or Custom**
   - Click **Start Scan**
4. Review results:
   - Raw scan output
   - AI-generated analysis (if Gemini API key is configured)
   - Download reports (JSON format)

### Command Line Usage
Run a quick scan from the terminal:
```sh
python main.py example.com
```
Results are saved in the `reports/` directory.

## Scan Types
- **Basic Scan**: Nmap (port scan) + Gobuster (directory enumeration)
- **Full Scan**: Nmap + Gobuster + FFUF (fuzzing) + SQLMap (SQL injection)
- **Custom Scan**: Select specific tools for assessment

## Reports & Logging
- **Reports**: JSON files stored in `reports/`.
- **Logs**: Detailed logs in `logs/audit.log`.
- **AI Analysis**: If Gemini API is enabled, AI-generated insights are included.

## Security & Scope Control
Strict measures prevent unauthorized scanning:
- Only domains listed in `TARGET_DOMAINS` can be scanned.
- Only IPs within `TARGET_IPS` ranges can be scanned.
- Scanning outside the defined scope is restricted.

**Important:** Only scan targets with explicit permission.

## Troubleshooting
### Common Issues & Fixes
1. **Run diagnostic script:**
   ```sh
   python diagnose.py
   ```
2. **Check logs:**
   ```sh
   cat logs/audit.log
   ```
3. **Verify API keys and scope:**
   - Ensure Gemini API key is valid.
   - Confirm target is correctly defined.
4. **Resolve missing tools:** Follow external tool installation steps.

## Project Structure
```
security-scanner/
├── agent/
│   ├── agent_graph.py        # Main orchestration logic
│   ├── task_executor.py      # Tool execution functions
│   └── task_manager.py       # Task generation & scope control
├── reports/                  # Scan reports directory
├── logs/                     # Log files
├── app.py                    # Web interface (Streamlit)
├── config.py                 # Configuration management
├── diagnose.py               # Diagnostic utility
├── main.py                   # Command line interface
├── setup.py                  # Installation script
├── test_gemini_api.py        # API connectivity test
├── .env.example              # Example config file
└── requirements.txt          # Python dependencies
```

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a feature branch:
   ```sh
   git checkout -b feature-name
   ```
3. Commit changes:
   ```sh
   git commit -m "Add feature"
   ```
4. Push and submit a pull request.

## License
This project is licensed under the **MIT License**.

## Disclaimer
**This tool is strictly for authorized security testing. Unauthorized use may be illegal. Always obtain permission before scanning any system.**

## Contact
For support or inquiries:
- **Email**: debasishtripathy7987@gmail.com
- **GitHub Issues**: [https://github.com/debasishtripathy13/security_scanner/issues](https://github.com/debasishtripathy13/security_scanner/issues)

---
Developed by **Debasish Tripathy** © 2025 | For educational purposes only

### AI Generated report analysis
![Screenshot_2025-02-28_19_15_27](https://github.com/user-attachments/assets/a37e20f0-71c0-4529-8679-4b37a9d6eef0)

### Application
![Screenshot_2025-02-28_19_15_32](https://github.com/user-attachments/assets/0424618c-69bc-4850-9b49-a79058397e94)

### Easy JSON Downloader
![Screenshot_2025-02-28_19_15_51](https://github.com/user-attachments/assets/25f44401-a825-4031-8cce-c789aac219f3)



