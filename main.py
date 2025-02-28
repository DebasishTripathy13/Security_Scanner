import os
import sys  
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from agent.agent_graph import run_agent  

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <target>")
        sys.exit(1)  

    target = sys.argv[1]
    print(f"Starting scan on: {target}")
    
    results = run_agent(target)
    
    print("Scan completed. Check reports/final_report.json for details.")