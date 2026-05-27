# Spatial AI Interface — Full MVP Scaffold

This scaffold gives you:

* frontend/

  * React
  * Vite
  * TypeScript
  * Tailwind
  * tldraw canvas
  * AI generation UI

* backend/

  * FastAPI
  * WebSockets
  * AI orchestration
  * Groq routing
  * Ollama integration

* ai-core/

  * tool switching
  * structured output
  * routing logic

The goal:

User draws → AI understands → AI generates UI → frontend renders it live.

---

# PROJECT STRUCTURE

```txt
project-root/
│
├── frontend/
├── backend/
├── ai-core/
└── README.md
```

---

# FRONTEND SETUP

## 1. CREATE FRONTEND

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
```

---

## 2. INSTALL DEPENDENCIES

```bash
npm install
npm install tailwindcss @tailwindcss/vite
npm install tldraw
npm install zustand
npm install framer-motion
npm install lucide-react
npm install axios
npm install react-hot-toast
```

---

# frontend/vite.config.ts

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

---

# frontend/src/index.css

```css
@import "tailwindcss";

html,
body,
#root {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: #0f0f0f;
  color: white;
  font-family: Inter, sans-serif;
}
```

---

# frontend/src/main.tsx

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

---

# frontend/src/store/useAppStore.ts

```ts
import { create } from 'zustand'

interface GeneratedUI {
  type: string
  components: any[]
}

interface AppState {
  generatedUI: GeneratedUI | null
  setGeneratedUI: (ui: GeneratedUI) => void
}

export const useAppStore = create<AppState>((set) => ({
  generatedUI: null,
  setGeneratedUI: (ui) => set({ generatedUI: ui }),
}))
```

---

# frontend/src/components/GeneratedRenderer.tsx

```tsx
import { useAppStore } from '../store/useAppStore'

export default function GeneratedRenderer() {
  const { generatedUI } = useAppStore()

  if (!generatedUI) return null

  return (
    <div className="absolute right-0 top-0 h-full w-[420px] bg-zinc-950 border-l border-zinc-800 overflow-auto p-4">
      <h2 className="text-xl font-bold mb-4">Generated Interface</h2>

      {generatedUI.components?.map((component, index) => {
        if (component.type === 'chart') {
          return (
            <div
              key={index}
              className="bg-zinc-900 rounded-xl p-4 mb-4"
            >
              <div className="h-40 bg-zinc-800 rounded-lg" />
              <p className="mt-2 text-sm text-zinc-400">
                Chart Component
              </p>
            </div>
          )
        }

        if (component.type === 'button') {
          return (
            <button
              key={index}
              className="bg-white text-black px-4 py-2 rounded-lg mr-2 mb-2"
            >
              {component.label}
            </button>
          )
        }

        return (
          <div
            key={index}
            className="bg-zinc-900 rounded-xl p-4 mb-4"
          >
            {component.type}
          </div>
        )
      })}
    </div>
  )
}
```

---

# frontend/src/components/Toolbar.tsx

```tsx
import axios from 'axios'
import { useAppStore } from '../store/useAppStore'
import toast from 'react-hot-toast'

export default function Toolbar({ editor }: any) {
  const { setGeneratedUI } = useAppStore()

  const generateUI = async () => {
    try {
      const shapes = editor.getCurrentPageShapes()

      const payload = {
        shapes,
      }

      const response = await axios.post(
        'http://localhost:8000/generate',
        payload
      )

      setGeneratedUI(response.data)

      toast.success('Interface generated!')
    } catch (err) {
      console.error(err)
      toast.error('Generation failed')
    }
  }

  return (
    <div className="absolute top-4 left-4 z-50 flex gap-2">
      <button
        onClick={generateUI}
        className="bg-white text-black px-4 py-2 rounded-xl font-semibold"
      >
        Generate Interface
      </button>
    </div>
  )
}
```

---

# frontend/src/App.tsx

```tsx
import { Tldraw, useEditor } from 'tldraw'
import 'tldraw/tldraw.css'
import GeneratedRenderer from './components/GeneratedRenderer'
import Toolbar from './components/Toolbar'
import { Toaster } from 'react-hot-toast'

function CanvasUI() {
  const editor = useEditor()

  return <Toolbar editor={editor} />
}

export default function App() {
  return (
    <div className="w-screen h-screen relative bg-black">
      <Toaster />

      <div className="absolute inset-0">
        <Tldraw>
          <CanvasUI />
        </Tldraw>
      </div>

      <GeneratedRenderer />
    </div>
  )
}
```

---

# BACKEND SETUP

## CREATE BACKEND

```bash
mkdir backend
cd backend
python -m venv venv
```

---

## INSTALL PYTHON DEPENDENCIES

```bash
pip install fastapi uvicorn python-dotenv requests pydantic websockets
```

---

# backend/.env

```env
GROQ_API_KEY=YOUR_GROQ_KEY
OLLAMA_URL=http://localhost:11434
```

---

# backend/app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_router import route_request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    shapes: list

@app.post('/generate')
async def generate(req: GenerateRequest):
    result = route_request(req.shapes)
    return result
```

---

# backend/app/ai_router.py

```python
from spatial_parser import parse_spatial_intent
from groq_client import generate_interface


def route_request(shapes):
    parsed = parse_spatial_intent(shapes)

    interface = generate_interface(parsed)

    return interface
```

---

# backend/app/spatial_parser.py

```python

def parse_spatial_intent(shapes):
    parsed = {
        "layout": "dashboard",
        "components": [],
    }

    for shape in shapes:
        shape_type = shape.get('type')

        if shape_type == 'geo':
            parsed['components'].append({
                "type": "chart"
            })

        if shape_type == 'text':
            parsed['components'].append({
                "type": "button",
                "label": shape.get('props', {}).get('text', 'Button')
            })

    return parsed
```

---

# backend/app/groq_client.py

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')


def generate_interface(parsed_intent):
    prompt = f'''
    You are an AI interface generator.

    Convert this spatial intent into structured JSON.

    Intent:
    {parsed_intent}

    Return ONLY valid JSON.
    '''

    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.2
        }
    )

    data = response.json()

    content = data['choices'][0]['message']['content']

    try:
        import json
        return json.loads(content)
    except Exception:
        return {
            "type": "dashboard",
            "components": [
                {
                    "type": "chart"
                }
            ]
        }
```

---

# OLLAMA INTEGRATION

# backend/app/ollama_client.py

```python
import requests

OLLAMA_URL = 'http://localhost:11434/api/generate'


def ollama_reason(prompt, model='llama3'):
    response = requests.post(
        OLLAMA_URL,
        json={
            'model': model,
            'prompt': prompt,
            'stream': False
        }
    )

    return response.json()['response']
```

---

# HYBRID TOOL SWITCHING

# backend/app/tool_switcher.py

```python
from ollama_client import ollama_reason


def choose_model(task_description):
    routing_prompt = f'''
    Decide which system should handle this.

    Return ONLY:
    GROQ
    or
    OLLAMA

    Task:
    {task_description}
    '''

    decision = ollama_reason(routing_prompt)

    return decision.strip()
```

---

# RUN BACKEND

```bash
cd backend/app
uvicorn main:app --reload
```

---

# RUN FRONTEND

```bash
cd frontend
npm run dev
```

---

# YOUR FIRST MVP FLOW

1. User draws layout.
2. Frontend serializes shapes.
3. Backend parses intent.
4. Tool switcher selects AI.
5. AI generates structured UI.
6. Frontend renders live interface.

---

# NEXT THINGS TO BUILD

## 1. Better Spatial Understanding

You currently only classify:

* geo
* text

Next:

* arrows
* hierarchy
* grouping
* layout zones
* flow structures

---

## 2. Incremental Updates

Instead of regenerating entire UI:

* regenerate selected region only.

VERY IMPORTANT.

---

## 3. Live Streaming

Use:

* WebSockets
* token streaming
* progressive rendering

---

## 4. Multimodal Vision

Take canvas snapshots.
Send to multimodal models.

This becomes extremely powerful.

---

## 5. Scene Graphs

Convert canvas into:

```json
{
  "nodes": [],
  "relationships": []
}
```

instead of raw shapes.

This dramatically improves reasoning.

---

# IMPORTANT DESIGN PRINCIPLE

DO NOT make:

* a chatbot with a canvas.

Make:

* a spatial cognition engine.

The canvas is the interface.

AI should feel embedded INTO the space.

---

# MOST IMPORTANT THING TO OPTIMIZE

Optimize for:

"I can think directly onto the canvas"

NOT:

"I can prompt an AI"

That distinction is your entire product.
