# cv-Analyzer

cv-Analyzer is a Django 4.2 project designed to process, analyze, and query CVs efficiently. The project includes **CV_Tracking_System**, an app that handles document processing, LLM integration, and a chatbot query system.

## Features

### 1. Document Processing
- Supports **PDF and Word documents**.
- Implements **OCR (Optical Character Recognition)** for scanned documents.
- Extracts structured information, including:
  - Personal Information
  - Education History
  - Work Experience
  - Skills
  - Projects
  - Certifications

### 2. LLM Integration
- Connects with **OpenAI GPT**.
- Utilizes **prompt engineering** to extract meaningful insights from CVs.
- Organizes and stores extracted information efficiently.
- Handles **API rate limiting and error management**.

### 3. Query System
- **Chatbot interface** to query CV information.
- Supports **natural language understanding**.
- Implements **context management** for follow-up queries.
- Common queries include:
  - Finding candidates with **specific skills**.
  - Comparing **education levels**.
  - Searching for **industry-specific experience**.
  - Identifying candidates matching **job requirements**.

## Installation & Setup

### 1. Clone the Repository
```bash
ttps://github.com/ow-tech/cv-Analyzer.git
cd cv_Analyzer
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
- Create a `.env` file in the root directory.
- Add the following:
```env
OPENAI_API_KEY=your-openai-api-key
```
- Check `.env_example` for reference.

### 5. Apply Migrations & Run Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Usage

### 1. Upload CVs
- Take sample CVs from the `data/sample_cvs/` folder (inside the root project directory).
- Uploading a CV **automatically creates a candidate entry and extracts structured data**.

### 2. View Candidates
- Visit the **Candidates Page** in the Django admin or frontend interface.

### 3. Query the Chat Assistant
- Go to the **Chat Assistant** page.
- Enter prompts like:
  - "Find candidates skilled in Python."
  - "Show candidates with at least 3 years of experience."
  - "Compare education levels of candidates."

## License
This project is licensed under the MIT License.

