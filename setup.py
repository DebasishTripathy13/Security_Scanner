import os
import shutil
import subprocess
import sys

def check_requirements():
    """Check if all required tools are installed."""
    try:
        # Check Python packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies.")
        return False

    # Check system tools
    tools = ['nmap', 'gobuster', 'ffuf', 'sqlmap']
    missing_tools = []
    
    for tool in tools:
        if shutil.which(tool) is None:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ The following tools are missing: {', '.join(missing_tools)}")
        print("Please install them manually or use the Docker container.")
        return False
    else:
        print("✅ All required security tools are installed.")
    
    # Create required directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Create wordlist directory if needed
    wordlist_dir = os.path.expanduser("~/wordlists")
    wordlist_file = os.path.join(wordlist_dir, "common.txt")
    
    if not os.path.exists(wordlist_file):
        os.makedirs(wordlist_dir, exist_ok=True)
        with open(wordlist_file, 'w') as f:
            f.write("admin\nlogin\nwp-admin\napi\ntest\ndev\n")
        print(f"✅ Created wordlist at {wordlist_file}")
    
    return True

def main():
    """Setup the security scanner application."""
    print("Setting up Security Scanner...")
    
    if not check_requirements():
        print("Setup failed. Please address the issues and try again.")
        return 1
    
    print("\n✅ Setup completed successfully!")
    print("\nYou can now run the application using:")
    print("  - For command line: python main.py <target>")
    print("  - For web interface: streamlit run app.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
