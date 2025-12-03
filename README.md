# Conversational Insights Generator  
### FastAPI + Gemini + PostgreSQL (Single-File Submission)

This project is a complete end-to-end pipeline that analyzes customer debt-collection call transcripts using Google’s Gemini API and stores structured insights in PostgreSQL.


## 📁 **Refer Submissions folder for all related docs and code**

---

## 🚀 **What the API Does**

1. Accepts a **raw Hinglish call transcript**  
2. Sends it to **Gemini 2.0 Flash Lite** using a strict JSON schema  
3. Extracts:
   - `customer_intent`
   - `sentiment` (“Positive”, “Neutral”, “Negative”)
   - `action_required` (boolean)
   - `summary`
4. Stores insights in a PostgreSQL table `call_records`  
5. Returns `{ id, insights }` as JSON  

All logic is packaged inside **`assignment.py`**.

---

## ⚙️ **Technology Stack**

| Layer | Technology |
|------|------------|
| API | FastAPI |
| LLM | Google Gemini (`gemini-2.0-flash-lite`) |
| Database | PostgreSQL + `asyncpg` |
| Models | Pydantic |
| Testing | pytest |
| Runtime | Uvicorn |

---

## 🔧 **Setup Instructions**

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure PostgreSQL
Create the database:

``CREATE DATABASE calls_db;``

### 3️⃣ Create your .env

Create a file named .env in the root folder:

``DATABASE_URL=postgresql://postgres:<yourpassword>@localhost:5432/calls_db``

``GEMINI_API_KEY=<your-gemini-api-key>``

``GEMINI_MODEL_NAME=gemini-2.0-flash-lite``


### ▶️ Run the API

Start the FastAPI server:

``uvicorn assignment:app --reload --port 8000``
If successful, you'll see:
Application startup complete.

### 🧪 Test Using Swagger UI /curl(Recommended)

Visit:
👉`` http://127.0.0.1:8000/docs``

Steps:

1.Open POST /analyze_call

2.Click Try it out

3.Enter this body:
json
;
``{
  "transcript": "Agent: Hello, customer: I want to make a payment next week."
}``
4.Click Execute

5.You should see output as:

{
  "id": 1,
  "insights": {
    "customer_intent": "...",
    "sentiment": "Neutral",
    "action_required": false,
    "summary": "..."
  }
}



### ▶️Store the Transcripts and responses in sql

``SELECT id, transcript, intent, sentiment, action_required, summary, created_at
FROM call_records
ORDER BY id;``

This is the query used to export:

➡️ call_records_insights_samples.csv

📄 Included CSV (10 Sample Calls)
The file:
call_records_insights_samples.csv
contains insights extracted from all 10 Hinglish call transcripts provided in the assignment.



## 🎥 YouTube Video Demonstration

**Video Link:**  
➡️ [https://youtu.be/hHcEZNZIDHA](https://youtu.be/hHcEZNZIDHA)


### 📘 Final Project Report 

Under the submissions folder



