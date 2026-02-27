# HMI Analyzer — FastAPI + HTML

Versión migrada de Streamlit a FastAPI con frontend HTML/CSS puro.  
Control total del diseño. Funcionalidad idéntica a la versión original.

---

## Estructura del proyecto

```
hmi-analyzer/
├── main.py              ← Backend Python (FastAPI + OpenAI)
├── requirements.txt     ← Dependencias
├── static/
│   └── index.html       ← Frontend completo (HTML + CSS + JS)
└── icons/               ← Copia aquí tus SVG de puentes (opcional)
```

---

## Cómo ejecutarlo en local

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Añadir tu API key de OpenAI

```bash
# Mac / Linux
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
```

### 3. Arrancar el servidor

```bash
uvicorn main:app --reload
```

Abre http://localhost:8000 en tu navegador. ¡Listo!

---

## Despliegue en Render (gratuito / de pago)

1. Sube el proyecto a un repositorio GitHub
2. Ve a https://render.com → New → Web Service
3. Conecta tu repositorio
4. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. En **Environment Variables** añade: `OPENAI_API_KEY` = tu clave
6. Deploy. Render te da una URL pública.

---

## Despliegue en Railway

1. Sube el proyecto a GitHub
2. Ve a https://railway.app → New Project → Deploy from GitHub
3. En Variables añade `OPENAI_API_KEY`
4. En Settings → Networking → el puerto es el 8000

---

## Integrar en tu web corporativa

Tienes dos opciones:

### Opción A — Iframe
Incrusta la app en cualquier página de tu web:
```html
<iframe src="https://tu-app.render.com" width="100%" height="900px" frameborder="0"></iframe>
```

### Opción B — Dominio propio
En Render o Railway puedes añadir un dominio personalizado  
(ej: `analyzer.hmidesign.es`) en la sección Custom Domains.

---

## Personalizar el diseño

Todo el CSS está en `static/index.html` dentro del bloque `<style>`.  
Las variables de color están al inicio:

```css
:root {
  --blue: #1a56db;       /* Color principal */
  --gray-900: #1a1917;   /* Texto oscuro */
  /* ... */
}
```

Para cambiar fuentes, busca la línea `@import url(...)` y reemplaza  
`Sora` y `DM Mono` por las fuentes de tu identidad corporativa.

---

## ¿Diferencias con la versión Streamlit?

| | Streamlit | FastAPI + HTML |
|---|---|---|
| Control del diseño | Limitado | Total |
| Integración en web | Difícil | Iframe o dominio |
| Velocidad de carga | Más lenta | Más rápida |
| Lógica OpenAI | Igual | Igual (sin cambios) |
| Despliegue | Streamlit Cloud | Render, Railway, etc. |
