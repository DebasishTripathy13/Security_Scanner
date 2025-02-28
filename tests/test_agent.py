import pytest
from agent.task_manager import is_within_scope, generate_tasks
from agent.agent_graph import run_agent

def test_scope_enforcement():
    """
    Test the is_within_scope function to ensure that it correctly identifies allowed and disallowed targets.
    
    - "google.com" is expected to be within scope.
    - "mail.google.com" is expected to be out of scope based on our criteria.
    """
    # Assert that a direct match (google.com) is within scope
    assert is_within_scope("google.com") == True
    
    # Assert that a subdomain (mail.google.com) is not considered within scope
    # This assumes that our scope is limited to the exact domain provided
    assert is_within_scope("mail.google.com") == False

def test_generate_tasks():
    """
    Test the generate_tasks function to ensure it returns a non-empty task list for a valid target.
    
    - The tasks should include at least one task.
    - Verify that an Nmap task is included in the returned task list.
    """
    tasks = generate_tasks("google.com")
    
    # Ensure that some tasks are generated for the target
    assert len(tasks) > 0
    
    # Ensure that one of the tasks is for Nmap scanning
    assert any(task["tool"] == "nmap" for task in tasks)

def test_run_agent():
    """
    Test the run_agent function to verify that it returns results for all expected tools.
    
    - The results should contain keys for nmap, gobuster, ffuf, and sqlmap.
    - This test assumes that the run_agent function returns a dictionary with each tool's results.
    """
    results = run_agent("google.com")
    
    # Check that the scan results contain entries for each tool
    assert "nmap" in results
    assert "gobuster" in results
    assert "ffuf" in results
    assert "sqlmap" in results