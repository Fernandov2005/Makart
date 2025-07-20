# Makart - Particle Animation Studio

This project is a high-performance particle animation studio with a split front-end/back-end architecture.

- **Frontend**: Next.js 14, React, Tailwind CSS, deployed on Vercel.
- **Backend**: Python, Flask, Gunicorn, deployed on Render/Railway.

## ✨ Features

- **🎨 Particle Transformation**: Convert any painting into mesmerizing particle animations.
- **🌟 Glassmorphism Design**: Modern UI with white backgrounds and subtle glass effects.
- **🔐 Secure Authentication**: JWT-based authentication with a secure Flask backend.
- **🚀 Scalable Architecture**: Split front-end and back-end for better performance and scalability.
- **📱 Responsive Design**: Works perfectly on all devices.

## 🚀 Quick Start

### Frontend (Vercel)

1.  Navigate to the `frontend` directory: `cd frontend`
2.  Install dependencies: `npm install`
3.  Run the development server: `npm run dev`
4.  Open [http://localhost:3000](http://localhost:3000) to view the app.

### Backend (Render/Railway)

1.  Navigate to the `backend` directory: `cd backend`
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run the development server: `gunicorn 'api.index:app'`
5.  The backend will be running at [http://localhost:8000](http://localhost:8000).

## 🛠️ Deployment

### Frontend (Vercel)

-   Connect your GitHub repository to Vercel.
-   Set the root directory to `frontend`.
-   Vercel will automatically detect the Next.js app and deploy it.

### Backend (Render/Railway)

-   Connect your GitHub repository to Render or Railway.
-   Set the root directory to `backend`.
-   Use the following settings:
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn 'api.index:app'`

## 📄 License

This project is proprietary software for Makart particle animation services.

---

**Transform your art into magic with Makart Particle Animation Studio** ✨ 