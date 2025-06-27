# src/main.py

import streamlit as st
from snowflake.snowpark import Session
import toml # Used to read connection.toml
from finops_framework.core.data_fetcher import DataFetcher
from finops_framework.models.dashboard_configs import APP_THEME
from finops_framework.ui.base_components import display_error_box

st.set_page_config(
    page_title="Snowflake FinOps Dashboard",
    page_icon="❄️",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded" # Keep sidebar expanded by default
)

# Apply custom theme colors for basic elements
# For full theme control, you might also use a .streamlit/config.toml file
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {APP_THEME['background_color']};
    }}
    .sidebar .sidebar-content {{
        background-color: {APP_THEME['secondary_background_color']};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {APP_THEME['text_color']};
    }}
    .stTextInput>div>div>input {{
        color: {APP_THEME['text_color']};
    }}
    .stSelectbox>div>div>label {{
        color: {APP_THEME['text_color']};
    }}
    .stDateInput label {{
        color: {APP_THEME['text_color']};
    }}
    .stMarkdown {{
        color: {APP_THEME['text_color']};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("❄️ Snowflake FinOps Dashboard")
st.markdown("Optimize your Snowflake spending with actionable insights.")

# --- Snowpark Session Management ---
# This function establishes and caches the Snowpark session.
# It reads connection details from config/connection.toml for local development.
# IMPORTANT: For production deployments, strongly recommend using Streamlit Secrets Management (st.secrets).
@st.cache_resource # Cache the Snowpark session to avoid re-creating on every rerun
def get_snowpark_session() -> Session:
    """
    Establishes and returns a Snowpark session.
    Loads connection details from config/connection.toml.
    """
    try:
        # Load connection details from config/connection.toml
        # In a production Streamlit app, you should use st.secrets.
        # Example using st.secrets:
        # connection_parameters = st.secrets["snowflake"]
        
        # For this example, we load from TOML as planned earlier for setup ease.
        # Ensure connection.toml is correctly filled out.
        with open("config/connection.toml", "r") as f:
            config = toml.load(f)
        
        connection_parameters = config["snowflake"]

        st.spinner("Connecting to Snowflake...")
        session = Session.builder.configs(connection_parameters).create()
        st.success("Successfully connected to Snowflake!")
        return session
    except FileNotFoundError:
        st.error("`config/connection.toml` not found. Please create it with your Snowflake connection details.")
        st.stop() # Stop the app if config is missing
    except KeyError as e:
        st.error(f"Missing key in `config/connection.toml`: {e}. Please check your connection parameters.")
        st.stop()
    except Exception as e:
        display_error_box(f"Failed to connect to Snowflake: {e}")
        st.stop() # Stop the app if connection fails


# Initialize Snowpark Session and DataFetcher
session = get_snowpark_session()
data_fetcher = DataFetcher(session)

# Store data_fetcher and snowpark_session in st.session_state
# This makes them accessible to all multi-pages without re-initialization.
st.session_state.data_fetcher = data_fetcher
st.session_state.snowpark_session = session 

st.info("Use the sidebar to navigate through FinOps insights.")

# Introductory text for the main page
st.markdown("""
Welcome to your Snowflake FinOps Dashboard!
Navigate through the pages in the sidebar to explore different aspects of your Snowflake usage and cost.

**Get Started:**
1.  **Overview:** See your total credit consumption, estimated costs, and top cost drivers.
2.  **User 360:** Dive into specific user spending patterns, query performance, and potential optimizations.
3.  **Warehouse Insights:** Analyze warehouse utilization, identify idle time, and review auto-suspend settings.
""")

# Streamlit's multipage app structure automatically creates sidebar navigation
# for files placed within the `pages/` directory.
# You don't need explicit st.sidebar.page_link calls here.