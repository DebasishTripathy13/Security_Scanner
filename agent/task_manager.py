import logging
from config import ALLOWED_DOMAINS, ALLOWED_IPS

def is_within_scope(target):
    """
    Check if the given target (domain or IP) is within the allowed scope.

    The function ensures that:
    - Only allowed domains and IPs are processed.
    - Subdomains of allowed domains are considered within scope.
    - Protocols (http://, https://) are removed before checking.
    - Query parameters and paths are ignored for scope verification.
    """

    # Remove protocol (http:// or https://) if present
    if target.startswith(('http://', 'https://')):
        target = target.split('://')[-1]  # Extract the part after '://'

    # Remove any URL paths or query parameters
    target = target.split('/')[0].split('?')[0]  # Keep only the domain or IP

    # Normalize target: strip whitespace and convert to lowercase
    target = target.strip().lower()

    # Normalize allowed domains and IPs for comparison
    allowed_domains = [d.strip().lower() for d in ALLOWED_DOMAINS]
    allowed_ips = [ip.strip() for ip in ALLOWED_IPS]

    # Log the details for debugging
    logging.info(f"Checking scope for: {target}")
    logging.info(f"Allowed domains: {allowed_domains}")

    # Direct match check
    if target in allowed_domains or target in allowed_ips:
        return True

    # Check if the target is a subdomain of an allowed domain
    for domain in allowed_domains:
        if target.endswith(f".{domain}") or target == domain:
            return True

    # If none of the conditions matched, log a warning and return False
    logging.warning(f"Target {target} is out of the defined scope.")
    return False

def generate_tasks(target):
    """
    Generate a list of security scanning tasks for the given target.

    - Cleans up the target URL for scope verification.
    - Checks if the target is within the allowed scope.
    - Assigns appropriate scanning tools (Nmap, Gobuster, FFUF, SQLMap).
    - Ensures proper handling of protocols.

    Returns:
        List of dictionaries, where each dictionary contains:
        - "tool": The security tool to be used.
        - "target": The cleaned and formatted target URL.
    """

    # Extract the main domain or IP for scope checking (remove protocol and paths)
    check_target = target
    if check_target.startswith(('http://', 'https://')):
        check_target = check_target.split('://')[-1].split('/')[0]

    # Validate if the target is within the allowed scope
    if not is_within_scope(check_target):
        return []  # Return an empty list if out of scope

    # List to store the security tasks
    tasks = []

    # The base target (domain or IP without protocol)
    base_target = check_target

    # Construct a proper web target URL (default to HTTPS for security)
    web_target = f"https://{base_target}"

    # Add an Nmap scan for network reconnaissance
    tasks.append({"tool": "nmap", "target": base_target})

    # Add web-based scans using different tools
    tasks.extend([
        {"tool": "gobuster", "target": web_target},  # Directory brute-force
        {"tool": "ffuf", "target": web_target},      # Fuzzing
        {"tool": "sqlmap", "target": web_target}     # SQL injection testing
    ])

    return tasks