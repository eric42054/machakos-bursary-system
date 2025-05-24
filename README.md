
# 🏛️ Machakos County Bursary Management System

A web-based application to streamline bursary applications, approvals, and disbursement tracking for Machakos County. Built using Flask and designed as a final year project for a BSc in Software Development.

## 🚀 Features

- Online application form for students
- Admin and staff login system
- Document uploads (PDF/DOCX)
- Applicant eligibility evaluation logic
- Status tracking and reporting
- Role-based access control

## 📁 Project Structure

```
machakos-bursary-system/
│
├── backend/               # Main Flask app (imported in server.py)
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── ...
│
├── static/                # CSS, JS, images
├── templates/             # HTML templates (Jinja2)
├── server.py              # Entry point (runs the app)
└── requirements.txt       # Python dependencies
```

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite (via SQLAlchemy)
- **Frontend**: HTML5, CSS3, Bootstrap
- **Deployment**: Flask Dev Server

## ⚙️ How to Run

```bash
# Step 1: Clone the repository
git clone https://github.com/eric42054/machakos-bursary-system.git

# Step 2: Navigate into the project folder
cd machakos-bursary-system

# Step 3: Set up a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Run the app
python server.py
```

## 📷 Screenshots

*(Add images in a `screenshots/` folder and embed here)*  
Example:

```md
![Login Page](screenshots/login.png)
![Admin Dashboard](screenshots/dashboard.png)
```

## 👤 Author

**Eric Wambua Lavuta**  
📧 ericwambua2322@gmail.com  
📍 Nairobi, Kenya  
🎓 BSc Software Development – KCA University

## 📜 License

For academic use only.
