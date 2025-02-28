import subprocess  # For running shell commands
import logging  # For logging events and errors
from config import MAX_RETRIES, LOGS_DIR, REPORTS_DIR, LOG_FILE, WORDLIST_FILE  # Import path configurations
import os  # For file and directory operations
from pathlib import Path  # For handling file paths
import shutil  # For checking if required tools are installed
import json  # For handling JSON output from ffuf
from datetime import datetime  # For timestamping reports
import re  # For regex pattern matching
from urllib.parse import urlparse, quote  # For URL parsing and encoding

# Ensure the logs and reports directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Configure logging (logs will be written to logs/audit.log)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_wordlist_path():
    """Retrieve the path to the wordlist file, creating it if it does not exist."""
    wordlist_path = WORDLIST_FILE  # Use the path from config
    
    if not os.path.exists(wordlist_path):
        os.makedirs(os.path.dirname(wordlist_path), exist_ok=True)  # Create directory if needed
        with open(wordlist_path, 'w') as f:
            # Write common directory names to the wordlist
            f.write("admin\nlogin\nwp-admin\napi\ntest\ndev\n")
    
    return wordlist_path  # Return the path to the wordlist file

def run_command(command, retries=MAX_RETRIES):
    """Execute a shell command with retry logic and error handling."""
    attempt = 0
    while attempt < retries:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,  # Capture stdout and stderr
                text=True,
                timeout=300  # Set a timeout of 5 minutes
            )
            
            if result.returncode == 0:  # Check if command executed successfully
                logging.info(f"Command succeeded: {command}")
                return {"status": "success", "output": result.stdout}
            else:
                error_msg = f"Command failed: {result.stderr}"
                logging.error(error_msg)
                attempt += 1
                if attempt < retries:
                    logging.info(f"Retrying command ({attempt}/{retries}): {command}")
                else:
                    return {"status": "failed", "error": error_msg}
                    
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 300 seconds: {command}"
            logging.error(error_msg)
            attempt += 1
            if attempt < retries:
                logging.info(f"Retrying command ({attempt}/{retries}): {command}")
            else:
                return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Error executing command {command}: {str(e)}"
            logging.error(error_msg)
            attempt += 1
            if attempt < retries:
                logging.info(f"Retrying command ({attempt}/{retries}): {command}")
            else:
                return {"status": "failed", "error": error_msg}

def check_environment():
    """Verify that all required tools are installed, logging any missing ones."""
    tools = {
        'nmap': {
            'linux': 'sudo apt install nmap',
            'darwin': 'brew install nmap',
            'win32': 'choco install nmap'
        },
        'gobuster': {
            'linux': 'sudo apt install gobuster',
            'darwin': 'brew install gobuster',
            'win32': 'choco install gobuster'
        },
        'ffuf': {
            'linux': 'sudo apt install ffuf',
            'darwin': 'brew install ffuf',
            'win32': 'choco install ffuf'
        },
        'sqlmap': {
            'linux': 'sudo apt install sqlmap',
            'darwin': 'brew install sqlmap',
            'win32': 'choco install sqlmap'
        }
    }
    
    platform = os.sys.platform
    for tool, install_cmds in tools.items():
        if not shutil.which(tool):  # Check if the tool is installed
            install_cmd = install_cmds.get(platform, 'Unknown platform')
            logging.error(f"{tool} not found. Install with: {install_cmd}")
            return False
    return True

def run_nmap(target):
    """Run an Nmap scan on the target."""
    command = f"nmap -Pn {target}"
    return run_command(command)

def run_gobuster(target):
    """Run Gobuster for directory enumeration using a predefined wordlist."""
    wordlist = get_wordlist_path()
    
    # Fix double protocol issue
    target = target.replace('https://https://', 'https://')
    
    command = f"gobuster dir -u {target} -w {wordlist} -t 50"
    logging.info(f"Running gobuster with command: {command}")
    return run_command(command)

def run_ffuf(target):
    """Run FFUF for directory fuzzing with optimized settings."""
    wordlist = get_wordlist_path()
    
    # Ensure proper URL formatting
    if not target.startswith(('http://', 'https://')):
        target = f"https://{target}"
    
    # Fix double protocol issue
    target = target.replace('https://https://', 'https://')
    target = target.replace('http://http://', 'http://')
    
    # Ensure target ends with trailing slash
    if not target.endswith('/'):
        target = f"{target}/"
    
    # Create a unique output filename
    output_file = f"ffuf_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Build FFUF command with additional parameters
    command = (
        f"ffuf "
        f"-u {target}FUZZ "
        f"-w {wordlist} "
        f"-mc 200,301,302,403 "  # Match codes
        f"-c "  # Enable colors
        f"-v "  # Verbose output
        f"-r "  # Follow redirects
        f"-t 40 "  # Number of threads
        f"-timeout 10 "  # Timeout in seconds
        f"-o {output_file} "  # Save output to JSON
        f"-of json "  # Output format as JSON
        f"-recursion "  # Enable recursion
        f"-recursion-depth 2"  # Set recursion depth
    )
    
    logging.info(f"Running ffuf with command: {command}")
    
    # Execute the command
    result = run_command(command)
    
    # Try to read the JSON output file if it exists
    try:
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                ffuf_json = json.load(f)
                
                # Format the output for better readability
                formatted_output = []
                if "results" in ffuf_json:
                    for entry in ffuf_json["results"]:
                        url = entry.get("url", "N/A")
                        status = entry.get("status", "N/A")
                        length = entry.get("length", "N/A")
                        words = entry.get("words", "N/A")
                        lines = entry.get("lines", "N/A")
                        
                        formatted_output.append(
                            f"Found: {url}\n"
                            f"Status: {status}\n"
                            f"Length: {length}\n"
                            f"Words: {words}\n"
                            f"Lines: {lines}\n"
                            f"{'-' * 40}"
                        )
                
                if formatted_output:
                    result["output"] = "\n".join(formatted_output)
                else:
                    result["output"] = "No results found"
                    
            # Clean up the temporary file
            os.remove(output_file)
    except Exception as e:
        logging.error(f"Error processing ffuf output: {str(e)}")
        if result.get("status") == "success":
            result["output"] = result.get("output", "No results found")
    
    logging.info(f"FFUF output: {result.get('output', '')}")
    return result

def validate_sqlmap_url(url):
    """
    Validate and format a URL for use with SQLMap.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        tuple: (valid_url, error_message)
            - valid_url: Properly formatted URL or None if invalid
            - error_message: Error message if URL is invalid, None otherwise
    """
    logging.info(f"Validating URL for SQLMap: {url}")
    
    # Check if URL is empty
    if not url or url.strip() == "":
        return None, "URL cannot be empty"
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    
    # Remove double protocols if present
    url = url.replace('https://https://', 'https://')
    url = url.replace('http://http://', 'http://')
    
    # Parse the URL to validate its components
    try:
        parsed = urlparse(url)
        
        # Check if host exists
        if not parsed.netloc:
            return None, "Invalid URL format: missing host"
        
        # Check if URL has a path or query params (SQLMap needs something to test)
        if not parsed.path or parsed.path == "/":
            if not parsed.query:
                logging.warning("URL has no path or query parameters. SQLMap needs parameters to test.")
                return url, "Warning: URL has no parameters to test"
    except Exception as e:
        return None, f"URL parsing error: {str(e)}"
    
    # Check for common SQLi testable parameters
    sql_params = ['id', 'page', 'query', 'search', 'category', 'item', 'pid', 'cat', 'product']
    has_testable_param = False
    
    if parsed.query:
        query_params = parsed.query.split('&')
        for param in query_params:
            if '=' in param:
                param_name = param.split('=')[0].lower()
                if param_name in sql_params:
                    has_testable_param = True
                    break
    
    if not has_testable_param and parsed.query:
        logging.info("URL has query parameters but none are common SQL injection targets.")
    
    logging.info(f"Validated URL for SQLMap: {url}")
    return url, None

def run_sqlmap(target):
    """Run SQLMap with automated SQL injection testing."""
    # Validate the URL before running SQLMap
    valid_target, error = validate_sqlmap_url(target)
    
    if not valid_target:
        error_msg = f"Cannot run SQLMap: {error}"
        logging.error(error_msg)
        return {"status": "failed", "error": error_msg}
    
    if error:  # This means there was a warning but URL is still usable
        logging.warning(error)
    
    command = (
        f"sqlmap -u {valid_target} "
        "--batch "  # Run in batch mode (no user input)
        "--random-agent "  # Use a random user agent
        "--level 1 "  # Set testing level
        "--risk 1 "  # Set risk level
        "--threads 4 "  # Use multiple threads
        "--timeout 30"  # Set timeout
    )
    
    # Add parameter detection if no specific parameters found
    if "?" not in valid_target:
        command += " --forms"  # Test forms if no URL parameters
    
    logging.info(f"Running sqlmap with command: {command}")
    return run_command(command)