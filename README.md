# ◈ Chromaforge — Color Palette Generator

A beautiful, zero-dependency Python Flask app that generates harmonious color palettes from a base color or at random.

## Features

- 8 harmony modes: Complementary, Analogous, Triadic, Split-Complementary, Tetradic, Monochromatic, Shades, Pastel + Random
- Live color picker + hex input
- Adjustable swatch count (3–12)
- Click any swatch to copy its hex code
- Export palette as CSS variables, JSON, or hex list
- Palette history (last 8 generated)
- Zero external dependencies beyond Flask

---

## 🚀 Run Locally

### 1. Clone / download the project

```bash
git clone <your-repo-url>
cd color-palette-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the development server

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🐳 Run with Docker

### Build the image

```bash
docker build -t chromaforge .
```

### Run the container

```bash
docker run -p 8000:8000 chromaforge
```

Open your browser at **http://localhost:8000**

---

## ☁️ Deploy to Render (free)

1. Push the project to a GitHub repository.
2. Go to [https://render.com](https://render.com) and create a **New Web Service**.
3. Connect your GitHub repo.
4. Set the following:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
5. Click **Deploy**. Render will give you a public URL.

---

## ☁️ Deploy to Railway

1. Push the project to GitHub.
2. Go to [https://railway.app](https://railway.app) and create a **New Project → Deploy from GitHub**.
3. Select your repo.
4. Railway auto-detects the `Procfile` and deploys immediately.
5. Add a custom domain or use the generated Railway URL.

---

## ☁️ Deploy to Heroku

```bash
# Install Heroku CLI, then:
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

---

## ☁️ Deploy to Fly.io

```bash
# Install flyctl, then:
fly auth login
fly launch          # follow prompts, it detects Dockerfile automatically
fly deploy
fly open
```

---

## API Reference

### `POST /api/generate`

Generate a palette.

**Body (JSON):**
```json
{
  "mode":  "analogous",
  "color": "#3b82f6",
  "count": 6
}
```

**Modes:** `random`, `complementary`, `analogous`, `triadic`, `split-complementary`, `tetradic`, `monochromatic`, `shades`, `pastel`

**Response:**
```json
{
  "palette": [
    {
      "hex":  "#3b82f6",
      "rgb":  { "r": 59, "g": 130, "b": 246 },
      "hsl":  { "h": 217.2, "s": 91.2, "l": 59.8 },
      "name": "Blue"
    }
  ],
  "mode": "analogous",
  "base": "#3b82f6"
}
```

### `GET /api/modes`

Returns all available mode names.

---

## Project Structure

```
color-palette-generator/
├── app.py              # Flask app + all palette logic
├── requirements.txt
├── Procfile            # For Heroku / Railway
├── Dockerfile          # For Docker / Fly.io / Render
├── .gitignore
├── templates/
│   └── index.html      # Single-page UI
└── static/
    ├── css/style.css
    └── js/app.js
```
