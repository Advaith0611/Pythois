# TODO: Deploy Pythios to pythios.xyz

This project is now a Vite/React app, not a single hand-written HTML file. To upload it to the website you already connected to `pythios.xyz`, you publish the built files from `frontend/dist/`.

Important: GitHub Pages can host the frontend only. The app will still work because it has local browser fallback generation. If you want the FastAPI backend/Groq/Ollama generation live on the public site, host `backend/` separately later and set `VITE_API_URL` to that backend URL before building.

## Option A: Replace the HTML Repo With the Built Website

Use this if your existing GitHub repo already controls `pythios.xyz`.

### 1. Build the website locally

From this project folder:

```bash
cd frontend
npm install
npm run build
```

After this, Vite creates:

```txt
frontend/dist/
```

That folder contains the real deployable website:

```txt
frontend/dist/index.html
frontend/dist/assets/
```

### 2. Open your existing GitHub Pages repo

Go to the repo where you currently have the simple `index.html` file.

If you already have it cloned locally, open that folder.

If not, clone it:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 3. Delete the old website files in that repo

Delete the old simple `index.html` and any old asset files that belong to the previous site.

Keep these if they exist:

```txt
CNAME
.git/
README.md
```

Your `CNAME` file should contain:

```txt
pythios.xyz
```

### 4. Copy the new built files into the GitHub Pages repo

Copy everything inside:

```txt
Pythios/frontend/dist/
```

into the root of your GitHub Pages repo.

The GitHub Pages repo should now look roughly like:

```txt
index.html
assets/
CNAME
README.md
```

### 5. Commit and push

Inside the GitHub Pages repo:

```bash
git add .
git commit -m "Deploy Pythios website"
git push
```

### 6. Wait for GitHub Pages to update

Go to:

```txt
https://pythios.xyz
```

GitHub Pages can take a minute or two to refresh.

If it still shows the old page, hard refresh:

```txt
Cmd + Shift + R
```

or open the site in an incognito/private browser window.

## Option B: Use GitHub Actions to Deploy Automatically

Use this if you want every push to your project repo to rebuild and publish automatically.

### 1. Put this whole project in the GitHub repo

Your repo should include:

```txt
frontend/
backend/
ai-core/
README.md
TODO.md
```

### 2. Create this folder

```txt
.github/workflows/
```

### 3. Create this file

```txt
.github/workflows/deploy.yml
```

### 4. Add this workflow

```yaml
name: Deploy frontend to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Build frontend
        working-directory: frontend
        run: npm run build

      - name: Add custom domain
        run: echo "pythios.xyz" > frontend/dist/CNAME

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: frontend/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 5. Enable GitHub Pages for Actions

In GitHub:

1. Open your repo.
2. Go to `Settings`.
3. Go to `Pages`.
4. Under `Build and deployment`, set `Source` to `GitHub Actions`.
5. Save.

### 6. Push the workflow

```bash
git add .
git commit -m "Add GitHub Pages deployment"
git push
```

### 7. Check the deployment

In GitHub:

1. Open the repo.
2. Click `Actions`.
3. Open the latest deploy run.
4. Wait until it finishes successfully.
5. Visit `https://pythios.xyz`.

## Backend Deployment Later

The current public GitHub Pages deployment will run the frontend only.

To make the hosted site call the real FastAPI backend:

1. Deploy `backend/` to a service like Render, Railway, Fly.io, or a VPS.
2. Get the backend URL, for example:

```txt
https://api.pythios.xyz
```

3. In `frontend/.env.production`, add:

```env
VITE_API_URL=https://api.pythios.xyz
```

4. Rebuild and redeploy the frontend.

Until then, the site still works in the browser using the built-in local fallback generator.
