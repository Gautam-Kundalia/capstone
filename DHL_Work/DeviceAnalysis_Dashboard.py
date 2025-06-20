import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from datetime import datetime
import warnings
import time
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Network Device Analysis Dashboard",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling and animations
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
   
    @keyframes glow {
        from { text-shadow: 0 0 20px #fff; }
        to { text-shadow: 0 0 30px #3498db, 0 0 40px #3498db; }
    }
   
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
   
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeInUp 0.6s ease-out;
    }
   
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        animation: pulse 1s infinite;
    }
   
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
        animation: slideIn 0.8s ease-out;
    }
   
    .info-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #f1f8ff 100%);
        border-left: 5px solid #3498db;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        animation: fadeInUp 0.8s ease-out;
    }
   
    .upload-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .filter-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        color: white;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .filter-box h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .filter-container {
        margin: 1rem 0;
        padding: 0;
    }
   
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .compliance-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #e74c3c;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .compliance-success {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2ecc71;
        animation: fadeInUp 0.8s ease-out;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data(uploaded_file):
    """Load and process the network device data from uploaded file with progress tracking"""
    try:
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Load CSV
        status_text.text("🔄 Loading CSV file...")
        progress_bar.progress(20)
        time.sleep(0.5)
        df = pd.read_csv(uploaded_file)
        
        # Step 2: Remove null columns
        status_text.text("🧹 Cleaning data - removing empty columns...")
        progress_bar.progress(40)
        time.sleep(0.5)
        original_cols = len(df.columns)
        df = df.dropna(axis=1, how='all')
        removed_cols = original_cols - len(df.columns)
        
        # Step 3: Process CCG columns
        status_text.text("⚙️ Processing CCG Raw Data columns...")
        progress_bar.progress(60)
        time.sleep(0.5)
        ccg_columns = [col for col in df.columns if col.startswith('CCG Raw Data_')]
        for col in ccg_columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        # Step 4: Clean basic columns
        status_text.text("🔧 Finalizing data processing...")
        progress_bar.progress(80)
        time.sleep(0.5)
        if 'Host is online' in df.columns:
            df['Host is online'] = df['Host is online'].fillna(False)
        
        if 'IPv4 Address' in df.columns:
            df['IPv4 Address'] = df['IPv4 Address'].astype(str)
        
        # Step 5: Complete
        status_text.text("✅ Data processing complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show processing summary
        st.markdown(f"""
        <div class="info-box">
            <h4>📊 Data Processing Summary</h4>
            <ul>
                <li>✅ Loaded <strong>{len(df):,}</strong> device records</li>
                <li>🧹 Removed <strong>{removed_cols}</strong> empty columns</li>
                <li>⚙️ Processed <strong>{len(ccg_columns)}</strong> CCG data columns</li>
                <li>📋 Final dataset: <strong>{len(df.columns)}</strong> attributes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

def create_interactive_metrics(df, col_filters=None):
    """Create interactive overview metrics cards with consistent sizing"""
    # Apply filters if provided
    filtered_df = df.copy()
    if col_filters:
        for col, values in col_filters.items():
            if values and 'All' not in values:
                filtered_df = filtered_df[filtered_df[col].isin(values)]
   
    col1, col2, col3, col4, col5 = st.columns(5)
   
    with col1:
        total_devices = len(filtered_df)
        change = len(filtered_df) - len(df) if col_filters else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📱</h3>
            <h4>Total Devices</h4>
            <h2>{total_devices:,}</h2>
            <small>{'📈 +' + str(change) if change > 0 else '📉 ' + str(change) if change < 0 else '📊 All data'}</small>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        if 'Host is online' in filtered_df.columns:
            online_devices = filtered_df['Host is online'].sum()
            online_pct = (online_devices / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢</h3>
                <h4>Online Devices</h4>
                <h2>{online_devices:,}</h2>
                <small>📊 {online_pct:.1f}% online</small>
            </div>
            """, unsafe_allow_html=True)
   
    with col3:
        if 'Class Vendor' in filtered_df.columns:
            unique_vendors = filtered_df['Class Vendor'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏢</h3>
                <h4>Unique Vendors</h4>
                <h2>{unique_vendors:,}</h2>
                <small>📈 Vendor diversity</small>
            </div>
            """, unsafe_allow_html=True)
   
    with col4:
        if 'Function' in filtered_df.columns:
            unique_functions = filtered_df['Function'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚙️</h3>
                <h4>Device Functions</h4>
                <h2>{unique_functions:,}</h2>
                <small>🔧 Function types</small>
            </div>
            """, unsafe_allow_html=True)
   
    with col5:
        if 'Segment' in filtered_df.columns:
            unique_segments = filtered_df['Segment'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌐</h3>
                <h4>Network Segments</h4>
                <h2>{unique_segments:,}</h2>
                <small>🏗️ Network zones</small>
            </div>
            """, unsafe_allow_html=True)
   
    return filtered_df

def create_interactive_filters(df):
    """Create interactive filter section with consistent box sizing"""
    st.markdown('<div class="section-header">🔍 Interactive Filters</div>', unsafe_allow_html=True)
    
    # Create filter container
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # Create filter columns with consistent sizing
    col1, col2, col3, col4 = st.columns(4)
   
    filters = {}
   
    with col1:
        st.markdown('''
        <div class="filter-box">
            <h3>🟢 Device Status</h3>
            <div style="flex-grow: 1;">
        ''', unsafe_allow_html=True)
        
        if 'Host is online' in df.columns:
            online_options = st.multiselect(
                "Filter by status:",
                options=['Online', 'Offline'],
                default=['Online', 'Offline'],
                help="Filter devices by their online status",
                key="status_filter"
            )
            if online_options:
                status_map = {'Online': True, 'Offline': False}
                filters['Host is online'] = [status_map[opt] for opt in online_options]
        
        st.markdown('</div></div>', unsafe_allow_html=True)
   
    with col2:
        st.markdown('''
        <div class="filter-box">
            <h3>🏢 Vendors</h3>
            <div style="flex-grow: 1;">
        ''', unsafe_allow_html=True)
        
        if 'Class Vendor' in df.columns:
            vendor_options = st.multiselect(
                "Select vendors:",
                options=['All'] + sorted(df['Class Vendor'].dropna().unique().tolist()),
                default=['All'],
                help="Select specific vendors to analyze",
                key="vendor_filter"
            )
            if vendor_options and 'All' not in vendor_options:
                filters['Class Vendor'] = vendor_options
        
        st.markdown('</div></div>', unsafe_allow_html=True)
   
    with col3:
        st.markdown('''
        <div class="filter-box">
            <h3>⚙️ Functions</h3>
            <div style="flex-grow: 1;">
        ''', unsafe_allow_html=True)
        
        if 'Function' in df.columns:
            function_options = st.multiselect(
                "Device functions:",
                options=['All'] + sorted(df['Function'].dropna().unique().tolist()),
                default=['All'],
                help="Filter by device function categories",
                key="function_filter"
            )
            if function_options and 'All' not in function_options:
                filters['Function'] = function_options
        
        st.markdown('</div></div>', unsafe_allow_html=True)
   
    with col4:
        st.markdown('''
        <div class="filter-box">
            <h3>🛡️ Compliance</h3>
            <div style="flex-grow: 1;">
        ''', unsafe_allow_html=True)
        
        if 'Compliance Status' in df.columns:
            compliance_options = st.multiselect(
                "Compliance status:",
                options=['All'] + sorted(df['Compliance Status'].dropna().unique().tolist()),
                default=['All'],
                help="Filter by compliance status",
                key="compliance_filter"
            )
            if compliance_options and 'All' not in compliance_options:
                filters['Compliance Status'] = compliance_options
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return filters

def analyze_compliance_detailed(df):
    """Detailed compliance analysis matching the Python output"""
    results = {}
    
    # Credential vulnerability analysis
    cred_vuln_columns = [col for col in df.columns if 'Credential Vulnerability' in col]
    suspicious_devices_list = []
    
    for col in cred_vuln_columns:
        vulnerable_devices = df[df[col] == True]
        if len(vulnerable_devices) > 0:
            suspicious_devices_list.extend(vulnerable_devices.index.tolist())
    
    # Remove duplicates and get suspicious devices dataframe
    suspicious_devices_indices = list(set(suspicious_devices_list))
    suspicious_devices_df = df.loc[suspicious_devices_indices] if suspicious_devices_indices else pd.DataFrame()
    
    # Compliance status analysis
    if 'Compliance Status' in df.columns:
        compliance_counts = df['Compliance Status'].value_counts()
        non_compliant = df[df['Compliance Status'] != 'Compliant']
        
        results['total_devices'] = len(df)
        results['compliant_devices'] = len(df[df['Compliance Status'] == 'Compliant']) if 'Compliant' in compliance_counts else 0
        results['non_compliant_devices'] = len(non_compliant)
        results['compliance_rate'] = (results['compliant_devices'] / results['total_devices'] * 100) if results['total_devices'] > 0 else 0
        
        # Non-compliant device analysis
        if len(non_compliant) > 0:
            results['non_compliant_by_function'] = non_compliant['Function'].value_counts() if 'Function' in non_compliant.columns else pd.Series()
            results['non_compliant_by_vendor'] = non_compliant['Class Vendor'].value_counts() if 'Class Vendor' in non_compliant.columns else pd.Series()
            results['non_compliant_by_os'] = non_compliant['Operating System'].value_counts() if 'Operating System' in non_compliant.columns else pd.Series()
            results['non_compliant_sample'] = non_compliant[['Device', 'IPv4 Address', 'Function', 'Operating System', 'Class Vendor']].head(10) if all(col in non_compliant.columns for col in ['Device', 'IPv4 Address', 'Function', 'Operating System', 'Class Vendor']) else pd.DataFrame()
            results['non_compliant_full'] = non_compliant  # Full non-compliant devices data
    
    # Suspicious devices analysis
    results['suspicious_devices'] = len(suspicious_devices_df)
    results['suspicious_devices_full'] = suspicious_devices_df  # Full suspicious devices data
    results['online_devices'] = df['Host is online'].sum() if 'Host is online' in df.columns else 0
    results['online_rate'] = (results['online_devices'] / results['total_devices'] * 100) if results['total_devices'] > 0 else 0
    
    return results

def create_compliance_analysis(df):
    """Create comprehensive compliance analysis dashboard"""
    st.markdown('<div class="section-header">🛡️ Compliance Analysis Dashboard</div>', unsafe_allow_html=True)
    
    # Perform detailed compliance analysis
    compliance_results = analyze_compliance_detailed(df)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊</h3>
            <h4>Total Devices</h4>
            <h2>{compliance_results['total_devices']:,}</h2>
            <small>📈 Analyzed devices</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        compliance_rate = compliance_results.get('compliance_rate', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅</h3>
            <h4>Compliant</h4>
            <h2>{compliance_results.get('compliant_devices', 0):,}</h2>
            <small>📊 {compliance_rate:.1f}% compliant</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        non_compliant = compliance_results.get('non_compliant_devices', 0)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <h3>⚠️</h3>
            <h4>Non-Compliant</h4>
            <h2>{non_compliant:,}</h2>
            <small>🚨 Needs attention</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        online_rate = compliance_results.get('online_rate', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟢</h3>
            <h4>Online Rate</h4>
            <h2>{online_rate:.1f}%</h2>
            <small>📡 Network availability</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Compliance Status Overview
    if compliance_results.get('non_compliant_devices', 0) > 0:
        st.markdown(f"""
        <div class="compliance-alert">
            <h4>⚠️ COMPLIANCE ALERT</h4>
            <p><strong>{compliance_results['non_compliant_devices']}</strong> non-compliant devices detected that require immediate attention!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="compliance-success">
            <h4>✅ COMPLIANCE STATUS: EXCELLENT</h4>
            <p>All devices are compliant with security policies!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Analysis Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Compliance pie chart
        if 'Compliance Status' in df.columns:
            compliance_counts = df['Compliance Status'].value_counts()
            colors = ['#2ecc71' if 'Compliant' in str(x) else '#e74c3c' for x in compliance_counts.index]
            
            fig = go.Figure(data=[go.Pie(
                labels=compliance_counts.index,
                values=compliance_counts.values,
                hole=.3,
                marker_colors=colors,
                textinfo='label+percent+value',
                textfont_size=12
            )])
            
            fig.update_layout(
                title="🛡️ Compliance Status Distribution",
                height=400,
                title_font_size=16,
                annotations=[dict(text='Compliance<br>Overview', x=0.5, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Compliance by function
        if compliance_results.get('non_compliant_by_function') is not None and len(compliance_results['non_compliant_by_function']) > 0:
            non_comp_func = compliance_results['non_compliant_by_function']
            fig = px.bar(
                x=non_comp_func.values,
                y=non_comp_func.index,
                orientation='h',
                title="⚠️ Non-Compliant Devices by Function",
                color=non_comp_func.values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=400, title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("✅ No non-compliant devices to display by function")
    
    # Detailed Tables
    if compliance_results.get('non_compliant_devices', 0) > 0:
        st.markdown("### 📋 Non-Compliant Devices Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(compliance_results.get('non_compliant_by_os', pd.Series())) > 0:
                st.markdown("**By Operating System:**")
                os_df = pd.DataFrame({
                    'Operating System': compliance_results['non_compliant_by_os'].index,
                    'Count': compliance_results['non_compliant_by_os'].values
                })
                st.dataframe(os_df, use_container_width=True)
        
        with col2:
            if len(compliance_results.get('non_compliant_by_vendor', pd.Series())) > 0:
                st.markdown("**By Vendor:**")
                vendor_df = pd.DataFrame({
                    'Vendor': compliance_results['non_compliant_by_vendor'].index,
                    'Count': compliance_results['non_compliant_by_vendor'].values
                })
                st.dataframe(vendor_df, use_container_width=True)
        
        # Sample non-compliant devices
        if not compliance_results.get('non_compliant_sample', pd.DataFrame()).empty:
            st.markdown("**Sample Non-Compliant Devices:**")
            st.dataframe(compliance_results['non_compliant_sample'], use_container_width=True)
    
    # Export non-compliant devices functionality
    if compliance_results.get('non_compliant_devices', 0) > 0:
        st.markdown("### 📥 Export Non-Compliant Devices")
        col1, col2 = st.columns([3, 1])
        with col2:
            if not compliance_results.get('non_compliant_full', pd.DataFrame()).empty:
                non_compliant_csv = compliance_results['non_compliant_full'].to_csv(index=False)
                st.download_button(
                    label="📥 Export Non-Compliant Devices",
                    data=non_compliant_csv,
                    file_name=f"non_compliant_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download complete details of all non-compliant devices"
                )
    
    # Suspicious devices analysis with export functionality
    if compliance_results.get('suspicious_devices', 0) > 0:
        st.markdown(f"""
        <div class="compliance-alert">
            <h4>🔍 SUSPICIOUS DEVICE ANALYSIS</h4>
            <p>⚠️ <strong>{compliance_results['suspicious_devices']}</strong> devices detected with credential vulnerabilities</p>
            <p>These devices may be using commonly used credentials or have other security vulnerabilities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Export suspicious devices
        if not compliance_results.get('suspicious_devices_full', pd.DataFrame()).empty:
            col1, col2 = st.columns([3, 1])
            with col2:
                suspicious_csv = compliance_results['suspicious_devices_full'].to_csv(index=False)
                st.download_button(
                    label="📥 Export Suspicious Devices",
                    data=suspicious_csv,
                    file_name=f"suspicious_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download complete details of all suspicious devices"
                )

def create_dynamic_charts(df, chart_type="default"):
    """Create dynamic charts with improved vendor and network topology visualizations"""
   
    st.markdown('<div class="section-header">📊 Dynamic Visualizations</div>', unsafe_allow_html=True)
   
    # Chart type selector
    chart_types = {
        "Device Status Overview": "status",
        "Vendor Analysis": "vendor", 
        "Network Topology": "network",
        "Security Analysis": "security",
        "Performance Metrics": "performance",
        "Compliance Analysis": "compliance"
    }
   
    selected_chart = st.selectbox(
        "📊 Select Analysis Type:",
        options=list(chart_types.keys()),
        help="Choose different analysis perspectives"
    )
   
    chart_key = chart_types[selected_chart]
   
    if chart_key == "status":
        create_status_charts(df)
    elif chart_key == "vendor":
        create_vendor_charts_fixed(df)
    elif chart_key == "network":
        create_network_charts_fixed(df)
    elif chart_key == "security":
        create_security_charts(df)
    elif chart_key == "performance":
        create_performance_charts(df)
    elif chart_key == "compliance":
        create_compliance_analysis(df)

def create_status_charts(df):
    """Create status-related charts"""
    col1, col2 = st.columns(2)
   
    with col1:
        if 'Host is online' in df.columns:
            status_counts = df['Host is online'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=['🟢 Online' if x else '🔴 Offline' for x in status_counts.index],
                title="🔄 Real-time Device Status",
                color_discrete_sequence=['#2ecc71', '#e74c3c'],
                hole=0.4
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12,
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            fig.update_layout(
                height=400,
                title_font_size=16,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
   
    with col2:
        # Online Devices by Function chart
        if 'Function' in df.columns and 'Host is online' in df.columns:
            # Filter for online devices only
            online_devices = df[df['Host is online'] == True]
            
            if len(online_devices) > 0:
                # Extract device types from Function column
                function_data = online_devices['Function'].dropna()
                
                # Parse function strings to extract device types
                device_types = []
                for func in function_data:
                    if pd.notna(func):
                        func_str = str(func).lower()
                        if 'voip' in func_str or 'ip phone' in func_str:
                            device_types.append('IP Phone')
                        elif 'router' in func_str or 'switch' in func_str:
                            device_types.append('Router/Switch')
                        elif 'computer' in func_str:
                            device_types.append('Computer')
                        elif 'printer' in func_str:
                            device_types.append('Printer')
                        elif 'accessory' in func_str:
                            device_types.append('Accessory')
                        elif 'networking' in func_str:
                            device_types.append('Networking')
                        else:
                            device_types.append('Other')
                
                if device_types:
                    device_counts = pd.Series(device_types).value_counts()
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=device_counts.index,
                            y=device_counts.values,
                            marker_color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#95a5a6'][:len(device_counts)],
                            text=device_counts.values,
                            textposition='auto',
                        )
                    ])
                    fig.update_layout(
                        title="📱 Online Devices by Function",
                        xaxis_title="Device Function",
                        yaxis_title="Number of Online Devices",
                        height=400,
                        title_font_size=16,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📱 No function data available for online devices")
            else:
                st.info("📱 No online devices found")
        else:
            # Fallback to compliance chart if function data not available
            if 'Compliance Status' in df.columns:
                compliance_counts = df['Compliance Status'].value_counts()
                fig = go.Figure(data=[
                    go.Bar(
                        x=compliance_counts.index,
                        y=compliance_counts.values,
                        marker_color=['#2ecc71' if 'Compliant' in str(x) else '#e74c3c' for x in compliance_counts.index],
                        text=compliance_counts.values,
                        textposition='auto',
                    )
                ])
                fig.update_layout(
                    title="🛡️ Compliance Status Distribution",
                    xaxis_title="Compliance Status",
                    yaxis_title="Number of Devices",
                    height=400,
                    title_font_size=16
                )
                st.plotly_chart(fig, use_container_width=True)

def create_vendor_charts_fixed(df):
    """Create vendor analysis charts with fixed Operating System visualization"""
    col1, col2 = st.columns(2)
   
    with col1:
        if 'Class Vendor' in df.columns:
            vendor_counts = df['Class Vendor'].dropna().value_counts().head(10)
            fig = px.bar(
                x=vendor_counts.values,
                y=vendor_counts.index,
                orientation='h',
                title="🏢 Top 10 Device Vendors",
                color=vendor_counts.values,
                color_continuous_scale='viridis',
                text=vendor_counts.values
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                height=500,
                title_font_size=16,
                xaxis_title="Number of Devices",
                yaxis_title="Vendor"
            )
            st.plotly_chart(fig, use_container_width=True)
   
    with col2:
        if 'Operating System' in df.columns:
            # Filter out null/empty values and clean the data
            os_data = df['Operating System'].dropna()
            os_data = os_data[os_data != '']
            os_data = os_data[os_data != 'Unknown']
            
            if len(os_data) > 0:
                os_counts = os_data.value_counts().head(8)
                
                # Create a proper pie chart instead of sunburst for better visualization
                fig = px.pie(
                    values=os_counts.values,
                    names=os_counts.index,
                    title="💻 Operating System Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=10
                )
                fig.update_layout(
                    height=500, 
                    title_font_size=16,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💻 No Operating System data available for visualization")

def create_network_charts_fixed(df):
    """Create network topology charts with fixed Network Segment visualization"""
    col1, col2 = st.columns(2)
   
    with col1:
        if 'Segment' in df.columns:
            # Clean segment data
            segment_data = df['Segment'].dropna()
            segment_data = segment_data[segment_data != '']
            
            if len(segment_data) > 0:
                segment_counts = segment_data.value_counts().head(15)
                
                # Use bar chart for better reliability
                fig = px.bar(
                    x=segment_counts.values,
                    y=segment_counts.index,
                    orientation='h',
                    title="🌐 Network Segment Distribution",
                    color=segment_counts.values,
                    color_continuous_scale='Blues',
                    text=segment_counts.values
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(
                    height=500, 
                    title_font_size=16,
                    xaxis_title="Number of Devices",
                    yaxis_title="Network Segment"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🌐 No Network Segment data available for visualization")
   
    with col2:
        if 'Function' in df.columns:
            function_data = df['Function'].dropna()
            function_data = function_data[function_data != '']
            
            if len(function_data) > 0:
                function_counts = function_data.value_counts().head(10)
                fig = px.scatter(
                    x=range(len(function_counts)),
                    y=function_counts.values,
                    size=function_counts.values,
                    color=function_counts.values,
                    hover_name=function_counts.index,
                    title="⚙️ Device Function Bubble Chart",
                    color_continuous_scale='plasma'
                )
                fig.update_layout(
                    height=500,
                    title_font_size=16,
                    xaxis_title="Function Index",
                    yaxis_title="Device Count",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚙️ No Function data available for visualization")

def create_security_charts(df):
    """Create security analysis charts"""
    col1, col2 = st.columns(2)
   
    with col1:
        if 'Corporate/Guest Status' in df.columns:
            corp_guest = df['Corporate/Guest Status'].value_counts()
            fig = go.Figure(data=[
                go.Pie(
                    labels=corp_guest.index,
                    values=corp_guest.values,
                    hole=.3,
                    marker_colors=['#3498db', '#e67e22']
                )
            ])
            fig.update_layout(
                title="🏢 Corporate vs Guest Network",
                height=400,
                title_font_size=16,
                annotations=[dict(text='Network<br>Access', x=0.5, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
   
    with col2:
        # Create a security score based on available data
        security_metrics = []
        if 'Compliance Status' in df.columns:
            compliant_pct = (df['Compliance Status'] == 'Compliant').mean() * 100
            security_metrics.append(('Compliance', compliant_pct))
       
        if 'Host is online' in df.columns:
            online_pct = df['Host is online'].mean() * 100
            security_metrics.append(('Availability', online_pct))
       
        if security_metrics:
            metrics_df = pd.DataFrame(security_metrics, columns=['Metric', 'Score'])
            fig = px.bar(
                metrics_df,
                x='Metric',
                y='Score',
                title="🔒 Security Health Metrics",
                color='Score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig.update_layout(height=400, title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)

def create_performance_charts(df):
    """Create performance metrics charts"""
    col1, col2 = st.columns(2)
   
    with col1:
        if 'Discovery Score' in df.columns:
            discovery_data = df['Discovery Score'].dropna()
            if len(discovery_data) > 0:
                fig = px.histogram(
                    discovery_data,
                    nbins=20,
                    title="🔍 Device Discovery Score Distribution",
                    color_discrete_sequence=['#9b59b6']
                )
                fig.update_layout(
                    height=400,
                    title_font_size=16,
                    xaxis_title="Discovery Score",
                    yaxis_title="Number of Devices"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔍 No Discovery Score data available")
   
    with col2:
        if 'Classification Score' in df.columns:
            classification_data = df['Classification Score'].dropna()
            if len(classification_data) > 0:
                fig = px.box(
                    y=classification_data,
                    title="📊 Classification Score Distribution",
                    color_discrete_sequence=['#e67e22']
                )
                fig.update_layout(height=400, title_font_size=16)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No Classification Score data available")

def create_interactive_data_explorer(df):
    """Create interactive data explorer"""
    st.markdown('<div class="section-header">🔍 Interactive Data Explorer</div>', unsafe_allow_html=True)
   
    # Column selector
    available_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "📋 Select columns to display:",
        options=available_columns,
        default=available_columns[:10] if len(available_columns) > 10 else available_columns,
        help="Choose which columns to display in the data table"
    )
   
    if selected_columns:
        # Search functionality
        search_term = st.text_input("🔍 Search in data:", placeholder="Enter search term...")
       
        # Filter dataframe based on search
        display_df = df[selected_columns].copy()
        if search_term:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
       
        # Display count
        st.info(f"📊 Showing {len(display_df):,} records out of {len(df):,} total")
       
        # Interactive dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
       
        # Download functionality
        col1, col2 = st.columns(2)
        with col1:
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name=f"network_devices_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
       
        with col2:
            if st.button("📊 Generate Summary Report"):
                st.markdown("### 📋 Data Summary Report")
                summary_stats = display_df.describe(include='all')
                st.dataframe(summary_stats, use_container_width=True)

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-header">🖥️ Network Device Analysis Dashboard</div>', unsafe_allow_html=True)
   
    # File upload section with enhanced styling
    st.markdown("""
    <div class="upload-section">
        <h2>📁 Upload Your Network Device Data</h2>
        <p>Upload your CSV file containing network device information to begin interactive analysis</p>
    </div>
    """, unsafe_allow_html=True)
   
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your network devices CSV file to start the analysis"
    )
   
    if uploaded_file is None:
        # Show welcome message and instructions
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🎯 **Enhanced Dashboard Features**
           
            - **📊 Real-time Metrics:** Dynamic counters with smooth animations
            - **🔍 Smart Filtering:** Uniform filter boxes with consistent sizing  
            - **📈 Dynamic Charts:** Interactive visualizations with improved performance
            - **🛡️ Compliance Analysis:** Comprehensive security compliance monitoring
            - **📥 Export Functionality:** Download suspicious and non-compliant devices
            - **🔄 Live Updates:** All charts update automatically with your selections
            - **📋 Data Explorer:** Advanced search, filter, and export capabilities
            - **🎨 Enhanced UI:** Professional animations and responsive design
           
            ### 📈 **Analysis Capabilities:**
           
            - **Device Health:** Real-time online/offline status with detailed metrics
            - **Security Posture:** Advanced compliance tracking and vulnerability assessment
            - **Network Topology:** Enhanced segment distribution and infrastructure mapping
            - **Vendor Analysis:** Improved hardware standardization insights
            - **Performance Metrics:** Discovery confidence and classification accuracy
            - **Compliance Dashboard:** Detailed security compliance analysis with export options
           
            ### 🚀 **Get Started:**
            Simply upload your CSV file above and watch your data transform into actionable insights!
            """)
        return
   
    # Load and process data with enhanced progress tracking
    with st.spinner(""):
        df = load_and_process_data(uploaded_file)
   
    if df is None:
        st.error("❌ Failed to load data. Please check your CSV file format.")
        return
   
    # Success message with enhanced styling
    st.success(f"✅ Successfully loaded {len(df):,} devices with {len(df.columns)} attributes!")
   
    # Show data preview
    with st.expander("👀 Preview Your Data", expanded=False):
        st.dataframe(df.head(), use_container_width=True)
   
    # Interactive filters with improved styling
    filters = create_interactive_filters(df)
   
    # Apply filters and show metrics
    filtered_df = create_interactive_metrics(df, filters)
   
    # Dynamic charts with enhanced compliance analysis
    create_dynamic_charts(filtered_df)
   
    # Interactive data explorer
    create_interactive_data_explorer(filtered_df)
   
    # Enhanced real-time insights
    st.markdown('<div class="section-header">💡 Real-time Insights</div>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
   
    with col1:
        online_rate = (filtered_df['Host is online'].mean() * 100) if 'Host is online' in filtered_df.columns else 0
        vendor_count = filtered_df['Class Vendor'].nunique() if 'Class Vendor' in filtered_df.columns else 0
        compliance_status = "High" if online_rate > 90 else "Medium" if online_rate > 70 else "Low"
        segment_count = filtered_df['Segment'].nunique() if 'Segment' in filtered_df.columns else 0
        
        st.markdown(f"""
        <div class="info-box">
        <h4>🎯 Key Performance Indicators</h4>
        <ul>
        <li><strong>Network Health:</strong> {online_rate:.1f}% devices online</li>
        <li><strong>Vendor Diversity:</strong> {vendor_count} unique vendors</li>
        <li><strong>Security Level:</strong> {compliance_status} compliance rating</li>
        <li><strong>Infrastructure:</strong> {segment_count} network segments</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>📊 Dashboard Actions</h4>
        <p>🔍 <strong>Explore:</strong> Use consistent filter boxes for detailed analysis</p>
        <p>📈 <strong>Analyze:</strong> Switch to Compliance tab for security insights</p>
        <p>📥 <strong>Export:</strong> Download suspicious/non-compliant devices data</p>
        <p>🔄 <strong>Monitor:</strong> Real-time updates with smooth animations</p>
        </div>
        """, unsafe_allow_html=True)
   
    # Enhanced footer with compliance summary
    st.markdown("---")
    
    # Quick compliance summary
    if 'Compliance Status' in df.columns:
        compliance_rate = (df['Compliance Status'] == 'Compliant').mean() * 100
        non_compliant_count = len(df[df['Compliance Status'] != 'Compliant'])
        
        if non_compliant_count > 0:
            st.markdown(f"""
            <div class="compliance-alert">
                <h4>⚠️ Compliance Summary</h4>
                <p><strong>{non_compliant_count}</strong> non-compliant devices detected. 
                Switch to the <strong>Compliance Analysis</strong> tab for detailed investigation and export options.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="compliance-success">
                <h4>✅ Compliance Summary</h4>
                <p>Excellent! <strong>{compliance_rate:.1f}%</strong> compliance rate achieved. 
                All devices meet security requirements.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; color: #7f8c8d; padding: 1rem;">
        <p>🖥️ <strong>Enhanced Network Device Dashboard</strong> | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><em>Built with ❤️ using Streamlit • Enhanced animations • Professional compliance analysis • Export functionality</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()