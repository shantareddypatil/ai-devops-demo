# AI Project DevOps — Hands-on in VS Code (4 Hours)

**Goal:** Cohere API → Docker → GitHub Actions (CI/CD) → Live deploy.

**Rule:** Do ONE step. Pass the ✅ Check. Only then go to the next step.
If a check fails, stop and fix it (or ask Claude) before moving on.

---

## Step 0 — Setup (15 min)

Install these (skip what you already have):
- [Python 3.11+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — open it and keep it running
- [Git](https://git-scm.com/downloads)
- VS Code extensions: **Python**, **Docker**, **GitHub Actions**

Open VS Code → Terminal → New Terminal. Run:

```bash
python --version
docker --version
git --version
```

✅ **Check:** All three print a version number.

---

## Step 1 — Create the project folder (5 min)

```bash
mkdir ai-devops-demo
cd ai-devops-demo
code .
```

VS Code opens the folder. Create a folder `app` inside it.

✅ **Check:** You see `ai-devops-demo/app/` in the VS Code Explorer.

---

## Step 2 — Write the AI app (15 min)

Create file **`app/main.py`**:

```python
import os
from fastapi import FastAPI
from langchain_cohere import ChatCohere

app = FastAPI()
cohere_api_key = os.getenv("COHERE_API_KEY")
model = os.getenv("MODEL_NAME", "command-a-03-2025")
llm = ChatCohere(cohere_api_key=cohere_api_key, temperature=0.1, model=model) if cohere_api_key else None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ask")
def ask(q: str):
    if not llm:
        return {"answer": f"(demo mode) you asked: {q}"}
    response = llm.invoke(q)
    return {"answer": response.content}
```

Create file **`requirements.txt`** (in the root folder, not inside `app`):

```
fastapi
uvicorn
langchain-cohere
```

✅ **Check:** You have `app/main.py` and `requirements.txt`.

---

## Step 3 — Run it WITHOUT Docker first (15 min)

Why: make sure the code works before containerizing it.

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open in browser:
- http://localhost:8000/health
- http://localhost:8000/ask?q=hello

✅ **Check:** `/health` shows `{"status":"ok"}` and `/ask` shows a demo-mode answer.

Stop the server with `Ctrl + C`.

---

## Step 4 — Write the Dockerfile (15 min)

Create file **`Dockerfile`** (no extension) in the root:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create file **`.dockerignore`**:

```
.git
venv
__pycache__
.env
```

**Understand each line** (this is what interviewers and teammates ask):
- `FROM` → base image (Python pre-installed)
- `WORKDIR` → folder inside the container
- `COPY requirements.txt` first → Docker caches the pip install layer, so rebuilds are fast
- `CMD` → the command that starts the app
- `0.0.0.0` → listen on all interfaces so traffic from outside the container reaches it

✅ **Check:** `Dockerfile` and `.dockerignore` exist in the root.

---

## Step 5 — Build and run the container (20 min)

```bash
docker build -t ai-demo .
docker run -p 8000:8000 ai-demo
```

Open http://localhost:8000/health again.

Then open a **second terminal** and practice:

```bash
docker ps                      # list running containers
docker logs <container_id>     # see app logs
docker exec -it <container_id> sh   # go inside the container (type exit to leave)
docker stop <container_id>     # stop it
```

✅ **Check:** App works from Docker, and you ran all 4 commands above.

---

## Step 6 — Secrets the right way (15 min)

Never put API keys in code or in the Docker image.

Create file **`.env`** in the root:

```
COHERE_API_KEY=your_real_key_here
MODEL_NAME=command-a-03-2025
```

Create file **`.gitignore`**:

```
venv
__pycache__
.env
```

Run with the key injected at runtime:

```bash
docker run -p 8000:8000 --env-file .env ai-demo
```

Open http://localhost:8000/ask?q=what is devops

✅ **Check:** You get a real AI answer (or demo mode if you have no key — that's fine too). `.env` is listed in `.gitignore`.

---

## Step 7 — Push to GitHub (15 min)

1. Create a new **public** repo on GitHub named `ai-devops-demo` (lowercase, no README).
2. In the VS Code terminal:

```bash
git init
git add .
git commit -m "AI app with Docker"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-devops-demo.git
git push -u origin main
```

✅ **Check:** Code is visible on GitHub, and **`.env` is NOT there**. (If it is, delete the repo and rotate your API key.)

---

## Step 8 — CI/CD with GitHub Actions (30 min)

Create folders `.github/workflows/` and file **`.github/workflows/ci.yml`**:

```yaml
name: build-and-push
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

Push it:

```bash
git add .
git commit -m "Add CI pipeline"
git push
```

Go to GitHub → your repo → **Actions** tab → watch the run.

**Understand it:**
- `on: push` → pipeline triggers on every push to main
- `checkout` → pulls your code onto GitHub's machine
- `login-action` → logs into GitHub's container registry (GHCR)
- `build-push-action` → builds your Dockerfile and pushes the image

✅ **Check:** Green tick in Actions. Your image appears under your GitHub profile → **Packages**.

---

## Step 9 — Break it on purpose (15 min)

Best way to learn CI: see it fail.

In `Dockerfile`, change `python:3.11-slim` to `python:3.11-wrongtag`. Commit and push.

✅ **Check:** Actions shows a red ❌. Open the logs, find the error line, fix the Dockerfile, push again → green ✅.

---

## Step 10 — Deploy live on Render (30 min)

1. Sign up at https://render.com with GitHub.
2. **New → Web Service** → select `ai-devops-demo` repo.
3. Render detects the Dockerfile automatically.
4. **Instance type:** Free.
5. **Environment** → add `COHERE_API_KEY` = your key (and optionally `MODEL_NAME`).
6. **Advanced** → Health Check Path = `/health`.
7. Click **Deploy**.

Wait for the build logs to finish.

✅ **Check:** Open `https://<your-app>.onrender.com/ask?q=hello` from your phone. It works on the internet. 🎉

(Free tier sleeps when idle — first request may take ~50 seconds. That's normal.)

---

## Step 11 — Lock in the knowledge (20 min)

Say this flow out loud until you can do it without looking:

> **Code → GitHub → GitHub Actions builds the Docker image → pushed to registry (GHCR) → deployed on Render with secrets injected at runtime → health check monitors it.**

Be ready to answer:
- Why Docker? → Same environment everywhere; "works on my machine" problem solved.
- Why not put the API key in the image? → Anyone with the image could read it.
- What does the health check do? → Platform checks `/health`; if it fails, it restarts or blocks bad deploys.
- What happens when you push code? → Pipeline builds and publishes a new image automatically.

✅ **Check:** You can explain all 4 answers in your own words.

---

## Done ✅

You now have a real, working DevOps pipeline for an AI app.

**Next (after the deadline):** docker-compose (app + database), deploying to AWS, and Kubernetes basics.
