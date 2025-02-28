import streamlit as st
import json
import os
import glob
import time
from datetime import datetime
import pandas as pd
from config import REPORTS_DIR, ALLOWED_DOMAINS, ALLOWED_IPS
import google.generativeai as genai
from dotenv import load_dotenv
from agent.agent_graph import run_agent, execute_task

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("⚠️ GEMINI_API_KEY not found in environment. Summarization feature will be disabled.")

st.set_page_config(
    page_title="Security Scanner Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <div style='background-color:#1E3A8A; padding:10px; border-radius:10px'>
        <h1 style='color:white; text-align:center'>🛡️ Security Scanner Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

def load_reports():
    reports = []
    for report_file in glob.glob(os.path.join(REPORTS_DIR, "final_report_*.json")):
        filename = os.path.basename(report_file)
        timestamp_str = filename.replace("final_report_", "").replace(".json", "")
        
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            reports.append({
                "filename": filename,
                "path": report_file,
                "timestamp": timestamp,
                "date": timestamp.strftime("%Y-%m-%d"),
                "time": timestamp.strftime("%H:%M:%S"),
            })
        except Exception as e:
            st.error(f"Error parsing report file {filename}: {str(e)}")
    
    return sorted(reports, key=lambda x: x["timestamp"], reverse=True)

def summarize_with_gemini(content, tool_name):
    if not GEMINI_API_KEY:
        return "Gemini API key not configured. Cannot generate summary."
    
    try:
        prompt = f"""
        You are a cybersecurity expert analyzing scan results.
        
        Below are the scan results from {tool_name}:
        
        {content}
        
        Please provide a concise summary of the results, highlighting:
        1. The key findings (like open ports, vulnerable endpoints, potential security issues)
        2. Security implications of these findings
        3. Any recommended actions
        
        Format your response in clear bullet points.
        """
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def display_tool_results(results, tool_name):
    with st.expander(f"{tool_name.upper()} Results", expanded=False):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Raw Output")
            if "output" in results:
                st.code(results["output"], language="bash")
            elif "error" in results:
                st.error(results["error"])
            else:
                st.info("No output available")
        
        with col2:
            st.subheader("AI Analysis")
            if "output" in results and GEMINI_API_KEY:
                with st.spinner(f"Generating analysis for {tool_name} results..."):
                    summary = summarize_with_gemini(results["output"], tool_name)
                    st.markdown(summary)
            elif not GEMINI_API_KEY:
                st.info("Enable Gemini API to view AI analysis")
            else:
                st.info("No output to analyze")

tab_run, tab_reports = st.tabs(["Run Scan", "View Reports"])

with tab_run:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Target Configuration")
        
        target_type = st.radio("Target Type", ["Domain", "IP Address"])
        
        target_help = "Enter a domain name or IP address to scan" 
        if target_type == "Domain":
            target_help += f" (Allowed domains: {', '.join(ALLOWED_DOMAINS)})"
        else:
            target_help += f" (Allowed IPs: {', '.join(ALLOWED_IPS)})"
        
        target = st.text_input("Enter Target", help=target_help)
        
        is_valid_target = True
        if target:
            if target_type == "Domain" and target not in ALLOWED_DOMAINS:
                st.error(f"Domain not allowed. Please use one of: {', '.join(ALLOWED_DOMAINS)}")
                is_valid_target = False
            elif target_type == "IP Address" and not any(target.startswith(ip.split('/')[0]) for ip in ALLOWED_IPS):
                st.error(f"IP Address not allowed. Please use one in the allowed ranges")
                is_valid_target = False
        
        st.markdown("### Scan Type")
        
        scan_type = st.selectbox(
            "Select Scan Type",
            ["Basic", "Full", "Custom"]
        )
        
        if scan_type == "Basic":
            st.info("**Basic Scan includes:**\n- Nmap (Port scanning)\n- Gobuster (Directory enumeration)")
            selected_tools = ["nmap", "gobuster"]
        elif scan_type == "Full":
            st.info("**Full Scan includes:**\n- Nmap (Port scanning)\n- Gobuster (Directory enumeration)\n- FFuF (Fuzzing)\n- SQLMap (SQL injection testing)")
            selected_tools = ["nmap", "gobuster", "ffuf", "sqlmap"]
        elif scan_type == "Custom":
            st.info("**Custom Scan:** Select the tools you want to use")
            tools = {}
            tools["nmap"] = st.checkbox("Nmap", value=True, help="Port scanning tool")
            tools["gobuster"] = st.checkbox("Gobuster", value=True, help="Directory enumeration tool")
            tools["ffuf"] = st.checkbox("FFuF", help="Web fuzzing tool")
            tools["sqlmap"] = st.checkbox("SQLMap", help="SQL injection testing tool")
            selected_tools = [tool for tool, selected in tools.items() if selected]
        
        start_button = st.button(
            "🔍 Start Scan", 
            type="primary",
            disabled=not (target and is_valid_target and selected_tools)
        )
    
    with col2:
        st.markdown("### Scan Progress & Results")
        
        results_container = st.container()
        
        if start_button and target and is_valid_target and selected_tools:
            with results_container:
                with st.spinner(f"Scanning {target}... This may take a few minutes"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results_text = st.empty()
                    
                    results = {}
                    total_tools = len(selected_tools)
                    
                    for i, tool in enumerate(selected_tools):
                        status_text.text(f"Running {tool.upper()} scan...")
                        progress = (i / total_tools) * 100
                        progress_bar.progress(int(progress))
                        
                        result = execute_task({"tool": tool, "target": target})
                        results[tool] = result
                        
                        results_text.json(results)
                        time.sleep(0.5)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_filename = f"final_report_{timestamp}.json"
                    report_path = os.path.join(REPORTS_DIR, report_filename)
                    
                    os.makedirs(REPORTS_DIR, exist_ok=True)
                    with open(report_path, "w") as f:
                        json.dump(results, f, indent=4)
                    
                    progress_bar.progress(100)
                    status_text.text(f"✅ Scan completed! Report saved as {report_filename}")
                
                st.markdown("#### Detailed Results")
                tool_tabs = st.tabs([tool.upper() for tool in results.keys()])
                
                for i, (tool, tab) in enumerate(zip(results.keys(), tool_tabs)):
                    with tab:
                        display_tool_results(results[tool], tool)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Download Results as JSON",
                        data=json.dumps(results, indent=2),
                        file_name=f"scan_results_{timestamp}.json",
                        mime="application/json"
                    )
        else:
            st.info("Configure your scan settings and click 'Start Scan' to begin")
            
            with st.expander("How to use this tool"):
                st.markdown("""
                1. Select your target type (Domain or IP Address)
                2. Enter a valid target from the allowed list
                3. Choose a scan type or customize your tool selection
                4. Click 'Start Scan' to begin the security assessment
                5. View and export results when the scan completes
                """)

with tab_reports:
    st.markdown("### Past Scan Reports")
    
    reports = load_reports()
    
    if not reports:
        st.warning("No reports found in the reports directory.")
        selected_report = None
    else:
        report_options = [f"{r['date']} {r['time']} - {r['filename']}" for r in reports]
        selected_report_idx = st.selectbox("Select Report:", range(len(report_options)), 
                                          format_func=lambda i: report_options[i])
        selected_report = reports[selected_report_idx]
        
        st.info(f"Selected: {selected_report['filename']}")
        
        try:
            with open(selected_report['path'], 'r') as f:
                report_data = json.load(f)
            
            st.subheader("Overview")
            
            tool_tabs = st.tabs(["Summary"] + list(report_data.keys()))
            
            with tool_tabs[0]:
                st.markdown("### Scan Summary")
                
                status_data = []
                for tool, results in report_data.items():
                    status = "✅ Success" if results.get("status") == "success" else "❌ Failed"
                    status_data.append({
                        "Tool": tool.upper(),
                        "Status": status,
                        "Findings": "View details in tool tab" if status == "✅ Success" else results.get("error", "N/A")
                    })
                
                status_df = pd.DataFrame(status_data)
                st.dataframe(status_df, use_container_width=True)
                
                if GEMINI_API_KEY:
                    st.markdown("### AI-Generated Security Assessment")
                    
                    with st.spinner("Generating comprehensive security assessment..."):
                        full_report = ""
                        for tool, results in report_data.items():
                            if results.get("status") == "success" and "output" in results:
                                full_report += f"\n\n--- {tool.upper()} RESULTS ---\n{results['output']}\n"
                        
                        overall_summary = summarize_with_gemini(full_report, "all security tools")
                        st.markdown(overall_summary)
            
            for i, tool_name in enumerate(report_data.keys()):
                with tool_tabs[i+1]:
                    display_tool_results(report_data[tool_name], tool_name)
                        
        except Exception as e:
            st.error(f"Error loading report: {str(e)}")

with st.sidebar:
    st.header("Settings")
    
    st.markdown("---")
    st.subheader("AI Configuration")
    
    new_api_key = st.text_input("Gemini API Key:", 
                               value=GEMINI_API_KEY if GEMINI_API_KEY else "", 
                               type="password",
                               help="Enter your Gemini API key to enable AI summaries")
    
    if st.button("Save API Key"):
        os.environ["GEMINI_API_KEY"] = new_api_key
        genai.configure(api_key=new_api_key)
        st.success("API key updated! Refresh summaries to see changes.")
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
    **Security Scanner Dashboard**
    
    This tool helps you run security scans against allowed targets and analyze results using AI.
    
    For allowed targets only.
    Not for use on targets without proper authorization.
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; opacity: 0.7;'>
    <p>Security Scanner Dashboard By Debasish Tripathy</p>
    <p>© 2025 | For educational purposes only</p>
</div>
""", unsafe_allow_html=True)
