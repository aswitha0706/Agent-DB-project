# db-agent

An AI-powered web application to interact with structured salary data using natural language. Built using **LangChain**, **Groq API**, and **Streamlit**, it translates user questions into SQL queries and returns intelligent, explainable responses.

---

## 🚀 Key Features

- 💬 Ask questions in natural language (e.g., _"What is the highest salary in each department?"_)
- 🔁 Converts input into executable SQL queries
- 🧠 Uses Groq's **LLaMA3** and **Mixtral** models via API
- 🔎 Returns query answers with SQL + explanation
- 📊 Preview your dataset directly
- 📂 Automatically creates SQLite DB from CSV
- 🧰 Robust error handling and fallback support

---

## 🛠️ Tech Stack

| Component    | Tech Used                        |
|--------------|----------------------------------|
| Backend AI   | Groq LLM API (LLaMA3 / Mixtral)  |
| Agent Logic  | LangChain SQL Agent              |
| UI           | Streamlit                        |
| Database     | SQLite (from CSV file)           |
| Env Config   | Python `dotenv`                  |

---

## 📁 Project Structure

.
├── db/ # SQLite database gets created here
│ └── salary.db
├── data/
│ └── salaries_2023.csv # Your salary data CSV file
├── app.py # Streamlit app entry point
├── .env # Environment variables (e.g., GROQ_API_KEY)
└── README.md

yaml
Copy
Edit

---

## ✅ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-repo/sql-query-ai-agent.git
   cd sql-query-ai-agent
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure API key

Create a .env file and add your Groq API key:

env
Copy
Edit
GROQ_API_KEY=your_groq_api_key_here
Place your dataset

Ensure your salary dataset CSV is saved at:

bash
Copy
Edit
./data/salaries_2023.csv
Run the application

bash
Copy
Edit
streamlit run app.py
🤖 Available LLM Models
Model Name	Description
llama3-70b-8192	Best performance (default)
llama3-8b-8192	Lightweight, faster model
mixtral-8x7b-32768	Large context capabilities

To switch models, modify the model= parameter in ChatGroq().

💡 Sample Questions
What is the highest average salary by department?

How many employees earn more than $100,000?

Which department has the most employees?

What is the median salary in the company?

Show me the top 10 highest paid employees

🧪 Example Output
markdown
Copy
Edit
Final Answer: The department with the highest average salary is 'Engineering' with an average of $120,500.

Explanation:
I queried the `salaries_2023` table for department-wise average salaries and ordered them in descending order.
SQL Query:
SELECT department, AVG(base_salary) AS avg_salary 
FROM salaries_2023 
GROUP BY department 
ORDER BY avg_salary DESC 
LIMIT 1;
📌 Notes
The SQLite database is auto-generated from the provided CSV file.

Only SELECT queries are allowed — no INSERT, UPDATE, or DELETE.

All Groq LLM communication is used strictly for inference only.

The app runs locally and respects data privacy.

🙌 Credits
🚀 Groq API – Ultra-fast inference

🦜 LangChain – AI Agent framework

📊 Streamlit – Interactive UI

ℹ️ About
This tool empowers users to perform complex data queries without needing SQL skills, making structured data insights accessible to all.

javascript
Copy
Edit

Let me know if you want this saved as a downloadable `.md` file.
