# 🌾 KisanSathi AI – AI-Powered Smart Farming Platform

**Empowering Farmers with Artificial Intelligence, Smart Insights, and Digital Agriculture.**

KisanSathi AI is an intelligent agriculture platform designed to help farmers make better farming decisions using Artificial Intelligence, Machine Learning, and real-time weather intelligence.

The platform provides crop disease detection, yield prediction, weather-based recommendations, and a multilingual AI assistant to make modern agricultural knowledge accessible to farmers.

---

## 🚀 Key Features

### 1. 🌱 AI-Based Crop Disease Detection
- Upload crop or leaf images.
- Analyze images using a trained deep learning model.
- Identify potential crop diseases.
- Provide disease information and suggested solutions.

### 2. 🌦️ Weather Intelligence
- Get real-time weather information.
- Monitor temperature, humidity, and rainfall.
- Receive weather-based farming recommendations.
- Help farmers plan irrigation and agricultural activities.

### 3. 📊 Crop Yield Prediction
- Predict estimated crop yield using machine learning.
- Analyze relevant agricultural input data.
- Support better farming and production planning.

### 4. 🤖 Multilingual AI Assistant
- AI-powered agricultural chatbot.
- Supports farmer queries in multiple languages.
- Provides information about crops, diseases, and farming practices.
- Uses LLM and Retrieval-Augmented Generation (RAG) for contextual responses.

### 5. 💊 Smart Disease Advisory
- Provides information about detected diseases.
- Suggests possible preventive measures.
- Offers practical crop-care recommendations.
- Advisories are informational and should be verified with agricultural experts.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend | Django, FastAPI |
| Database | PostgreSQL |
| AI / ML | Python, TensorFlow, Scikit-learn |
| Deep Learning | CNN |
| Generative AI | LLM, RAG |
| Image Processing | OpenCV, Pillow |
| API Integration | REST API |
| Version Control | Git, GitHub |

---

## 🏗️ System Architecture

```text
                 FARMER / USER
                       |
                       v
              REACT FRONTEND
            TypeScript + Tailwind
                       |
                       v
                BACKEND APIs
                 Django / FastAPI
                       |
          +------------+------------+
          |            |            |
          v            v            v
       PostgreSQL   AI / ML      Weather API
                    Models
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Disease     Yield       AI Assistant
      Detection  Prediction      LLM + RAG
          |           |           |
          +-----------+-----------+
                      |
                      v
               SMART INSIGHTS
                      |
                      v
                 FARMER USER
```

---

## 📂 Project Structure

```text
KisanSathi-AI/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── assets/
│   │   └── App.tsx
│   └── package.json
│
├── backend/
│   ├── accounts/
│   ├── prediction/
│   ├── ai_assistant/
│   ├── weather/
│   ├── config/
│   ├── manage.py
│   └── requirements.txt
│
├── models/
│   ├── crop_disease_model.keras
│   └── class_names.json
│
├── datasets/
│
├── docs/
│
├── .gitignore
└── README.md
```

*Note: This is a suggested organizational structure. Adjust it to match the actual repository.*

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have installed:

- Python 3.10+
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/guptaamit9005-cmyk/KisanSathi-Ai.git

cd KisanSathi-Ai
```

### 2. Backend Setup

```bash
cd backend

python -m venv venv
```

Activate virtual environment:

**Windows:**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start Django server:

```bash
python manage.py runserver
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

### 4. Environment Variables

Create a `.env` file in the appropriate backend directory.

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

WEATHER_API_KEY=your_weather_api_key
```

**Important:** Never upload your `.env` file, API keys, passwords, or secret credentials to GitHub.

---

## 🎯 Project Objectives

- Make AI-powered agricultural technology accessible to farmers.
- Detect crop diseases at an early stage.
- Improve agricultural decision-making.
- Provide intelligent weather-based recommendations.
- Make agricultural information available in regional languages.
- Support farmers through AI-driven digital solutions.

---

## 🔮 Future Enhancements

- Voice-based agricultural assistant.
- More regional Indian language support.
- Integration with government agricultural schemes.
- Advanced crop recommendation system.
- Improved disease detection accuracy.
- Mobile application for farmers.
- Personalized farming recommendations.

---

## 🌍 Real-World Impact

KisanSathi AI aims to bridge the gap between modern AI technology and traditional agriculture.

By combining Machine Learning, Deep Learning, Generative AI, and weather intelligence, the platform aims to help farmers access useful agricultural insights and make informed decisions.

---

## 👨‍💻 Developed By

**Amit Kumar Gupta**

AI & ML Engineering Student | Developer | Technology Enthusiast

GitHub: https://github.com/guptaamit9005-cmyk

Project Repository: https://github.com/guptaamit9005-cmyk/KisanSathi-Ai

---

## ⭐ Support

If you find this project interesting, consider giving this repository a ⭐ on GitHub.

**KisanSathi AI – Smart Technology, Better Farming, Stronger Future. 🌾**

