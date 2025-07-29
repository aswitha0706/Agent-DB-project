import pandas as pd
import os
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

# Load environment variables
load_dotenv()

# Initialize Groq model
model = ChatGroq(
    model="llama3-70b-8192",  # You can also use "llama3-8b-8192" or "mixtral-8x7b-32768"
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0
)

# Path to your SQLite database file
database_filepath = "./db/salary.db"

# Create database and load data
@st.cache_data
def setup_database():
    engine = create_engine(f"sqlite:///{database_filepath}")
    file_url = "./data/salaries_2023.csv"
    os.makedirs(os.path.dirname(database_filepath), exist_ok=True)
    
    if os.path.exists(file_url):
        df = pd.read_csv(file_url).fillna(value=0)
        df.to_sql("salaries_2023", con=engine, if_exists="replace", index=False)
        return True, f"Database created successfully! Loaded {len(df)} records."
    else:
        return False, f"CSV file not found at {file_url}"

# Setup database
db_status, db_message = setup_database()

# SQL Agent Prompts
MSSQL_AGENT_PREFIX = """
You are an agent designed to interact with a SQL database.
## Instructions:
- Given an input question, create a syntactically correct {dialect} query
to run, then look at the results of the query and return the answer.
- Unless the user specifies a specific number of examples they wish to
obtain, **ALWAYS** limit your query to at most {top_k} results.
- You can order the results by a relevant column to return the most
interesting examples in the database.
- Never query for all the columns from a specific table, only ask for
the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it. If you get an error
while executing a query, rewrite the query and try again.
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database.
- DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS
OF THE CALCULATIONS YOU HAVE DONE.
- Your response should be in Markdown. However, **when running a SQL Query
in "Action Input", do not include the markdown backticks**.
Those are only for formatting the response, not for executing the command.
- ALWAYS, as part of your final answer, explain how you got to the answer
on a section that starts with: "Explanation:". Include the SQL query as
part of the explanation section.
- If the question does not seem related to the database, just return
"I don\'t know" as the answer.
- Only use the below tools. Only use the information returned by the
below tools to construct your query and final answer.
- Do not make up table names, only use the tables returned by any of the
tools below.
- As part of your final answer, please include the SQL query you used in code format

## Tools:
"""

MSSQL_AGENT_FORMAT_INSTRUCTIONS = """
## Use the following format:

Question: the input question you must answer.
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}].
Action Input: the input to the action.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question.

Example of Final Answer:
<=== Beginning of example

Action: query_sql_db
Action Input: 
SELECT TOP (10) [base_salary], [grade] 
FROM salaries_2023
WHERE state = 'Division'

Observation:
[(27437.0,), (27088.0,), (26762.0,), (26521.0,), (26472.0,), (26421.0,), (26408.0,)]
Thought: I now know the final answer
Final Answer: There were 27437 workers making 100,000.

Explanation:
I queried the `xyz` table for the `salary` column where the department
is 'IGM' and the date starts with '2020'. The query returned a list of tuples
with the base salary for each day in 2020. To answer the question,
I took the sum of all the salaries in the list, which is 27437.
I used the following query:

===> End of Example
"""

# Initialize SQL agent
@st.cache_resource
def create_sql_agent_cached():
    if db_status:
        db = SQLDatabase.from_uri(f"sqlite:///{database_filepath}")
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        
        sql_agent = create_sql_agent(
            prefix=MSSQL_AGENT_PREFIX,
            llm=model,
            toolkit=toolkit,
            top_k=30,
            verbose=True,
            format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS
        )
        return sql_agent
    return None

# Streamlit UI Configuration
st.set_page_config(
    page_title="SQL Query AI Agent",
    page_icon="🔍",
    layout="wide"
)

# Main Title
st.title("🔍 SQL Query AI Agent")
st.markdown("Ask questions about your salary data and get instant SQL-powered answers!")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Management
    if not os.environ.get("GROQ_API_KEY"):
        st.warning("⚠️ Groq API Key Required")
        api_key = st.text_input("Enter your Groq API Key:", type="password", help="Get your API key from console.groq.com")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("✅ API Key set successfully!")
            st.rerun()
    else:
        st.success("✅ API Key is configured")
    
    st.markdown("---")
    
    # Database Status
    st.header("📊 Database Status")
    if db_status:
        st.success("✅ Database loaded successfully")
    else:
        st.error("❌ Database setup failed")
        st.error(db_message)
    
    st.markdown("---")
    
    # Model Information
    st.header("🤖 Model Information")
    st.markdown("**Current Model:** llama3-70b-8192")
    st.markdown("**Available Models:**")
    st.markdown("- llama3-70b-8192 (Best performance)")
    st.markdown("- llama3-8b-8192 (Faster)")
    st.markdown("- mixtral-8x7b-32768 (Large context)")
    
    st.markdown("---")
    
    # Instructions
    st.header("📝 Instructions")
    st.markdown("1. Enter your Groq API key above")
    st.markdown("2. Ensure your CSV file is at `./data/salaries_2023.csv`")
    st.markdown("3. Ask questions in natural language")
    st.markdown("4. Get SQL-powered answers instantly")

# Main Interface
if not db_status:
    st.error("❌ Database not available. Please ensure your CSV file is located at `./data/salaries_2023.csv`")
    st.stop()

if not os.environ.get("GROQ_API_KEY"):
    st.warning("⚠️ Please provide your Groq API key in the sidebar to continue.")
    st.info("💡 You can get a free API key from [console.groq.com](https://console.groq.com)")
    st.stop()

# Create SQL agent
sql_agent = create_sql_agent_cached()

if not sql_agent:
    st.error("❌ Failed to initialize SQL agent. Please check your configuration.")
    st.stop()

# Query Input
question = st.text_input(
    "💬 Enter your query:",
    placeholder="e.g., What is the highest average salary by department?",
    help="Ask questions about the salary data in natural language"
)

# Action Buttons
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    run_query = st.button("🚀 Run Query", type="primary", use_container_width=True)
with col2:
    clear_query = st.button("🗑️ Clear", use_container_width=True)
with col3:
    if st.button("📊 View Data", use_container_width=True):
        try:
            sample_data = pd.read_sql("SELECT * FROM salaries_2023 LIMIT 5", con=create_engine(f"sqlite:///{database_filepath}"))
            st.subheader("📋 Sample Data")
            st.dataframe(sample_data)
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")

if clear_query:
    st.rerun()

# Query Processing
if run_query and question:
    with st.spinner("🔄 Processing your query..."):
        try:
            # Run the SQL agent
            response = sql_agent.invoke({"input": question})
            
            # Display the result
            st.markdown("---")
            st.markdown("### 📊 Results")
            st.markdown(response["output"])
            
            # Add copy button for the response
            st.markdown("---")
            with st.expander("📋 Copy Response"):
                st.code(response["output"], language="markdown")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔧 Troubleshooting"):
                st.markdown("**Possible solutions:**")
                st.markdown("- Check if your CSV file exists at `./data/salaries_2023.csv`")
                st.markdown("- Verify your Groq API key is valid and has sufficient credits")
                st.markdown("- Try rephrasing your question to be more specific")
                st.markdown("- Check if the question is related to the salary database")

elif run_query and not question:
    st.warning("⚠️ Please enter a question first!")

# Sample Questions Section
st.markdown("---")
with st.expander("💡 Sample Questions (Click to try)"):
    sample_questions = [
        "What is the highest average salary by department?",
        "How many employees earn more than $100,000?",
        "Which department has the most employees?",
        "What is the salary distribution across different job titles?",
        "Show me the top 10 highest paid employees",
        "What is the median salary in the company?",
        "Which job title has the lowest average salary?",
        "How many different departments are there in the dataset?"
    ]
    
    cols = st.columns(2)
    for i, sample in enumerate(sample_questions):
        col = cols[i % 2]
        with col:
            if st.button(f"🔹 {sample}", key=f"sample_{i}", use_container_width=True):
                st.session_state.selected_question = sample
                st.rerun()

# Handle selected sample question
if hasattr(st.session_state, 'selected_question'):
    question = st.session_state.selected_question
    del st.session_state.selected_question
    
    with st.spinner("🔄 Processing sample query..."):
        try:
            response = sql_agent.invoke({"input": question})
            st.markdown("---")
            st.markdown(f"### 📊 Results for: *{question}*")
            st.markdown(response["output"])
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 🔗 Powered By")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🚀 **[Groq API](https://groq.com)**  \nUltra-fast inference")
with col2:
    st.markdown("🦜 **[LangChain](https://langchain.com)**  \nAI agent framework")
with col3:
    st.markdown("📊 **[Streamlit](https://streamlit.io)**  \nInteractive web app")

# Additional Information
with st.expander("ℹ️ About This Application"):
    st.markdown("""
    This SQL Query AI Agent allows you to interact with your salary database using natural language queries. 
    
    **Features:**
    - Natural language to SQL conversion
    - Real-time query execution
    - Detailed explanations of results
    - Sample data preview
    - Error handling and troubleshooting
    
    **Data Source:** The application expects a CSV file at `./data/salaries_2023.csv` which is automatically 
    converted to a SQLite database for querying.
    
    **Security:** Your data remains local - only queries and results are sent to Groq's API for processing.
    """)
