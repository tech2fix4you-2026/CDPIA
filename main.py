import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="CDPIA - Bibliothèque IA")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/request-access", response_class=HTMLResponse)
async def request_access(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...)
):
    return templates.TemplateResponse(
        request=request, 
        name="success.html", 
        context={"first_name": first_name, "last_name": last_name, "email": email}
    )

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "app": "CDPIA"}
