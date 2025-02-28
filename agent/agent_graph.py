import json
import logging
import os
from datetime import datetime
from agent.task_manager import generate_tasks
from agent.task_executor import run_nmap, run_gobuster, run_ffuf, run_sqlmap
from config import REPORTS_DIR

def execute_task(task):
    """
    Executes a given security scanning task based on the tool specified.
    
    - Logs the execution details.
    - Calls the appropriate function based on the tool name.
    - Returns the output of the executed command.

    Args:
        task (dict): A dictionary containing the tool name and target.

    Returns:
        dict: The output of the tool execution, or an error message if the tool is unknown.
    """
    tool = task.get("tool")  
    target = task.get("target")  
    logging.info(f"Executing task: {tool} on target: {target}")

    if tool == "nmap":
        return run_nmap(target)
    elif tool == "gobuster":
        return run_gobuster(target)
    elif tool == "ffuf":
        return run_ffuf(target)
    elif tool == "sqlmap":
        return run_sqlmap(target)
    else:
        logging.error(f"Unknown tool specified: {tool}")
        return {"status": "failed", "error": f"Unknown tool specified: {tool}"}

def run_agent(target):
    """
    Main function that orchestrates the security scanning process.

    - Generates a list of tasks for the given target.
    - Executes each task sequentially.
    - Dynamically adds new tasks based on results.
    - Saves the final output as a JSON report.

    Args:
        target (str): The domain or IP address to be scanned.

    Returns:
        dict: A dictionary containing the results of the executed tasks.
    """
    tasks = generate_tasks(target)
    
    if not tasks:
        logging.error("No tasks generated. The target might be out of scope.")
        return {"error": "Target is out of scope or no valid tasks were generated."}
    
    results = {}  

    for task in tasks:
        output = execute_task(task)  
        results[task["tool"]] = output  

        if task["tool"] == "nmap" and "open" in output.get("output", ""):

            if "80/tcp" in output.get("output", ""):
                tasks.append({"tool": "gobuster", "target": f"http://{target}"})  
            if "443/tcp" in output.get("output", ""):
                tasks.append({"tool": "gobuster", "target": f"https://{target}"})  
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{REPORTS_DIR}/final_report_{timestamp}.json"

    os.makedirs(REPORTS_DIR, exist_ok=True)

    with open(report_filename, "w") as f:
        json.dump(results, f, indent=4)  
    
    logging.info(f"Final report saved to {report_filename}")  
    return results  