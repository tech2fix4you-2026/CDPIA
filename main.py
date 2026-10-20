import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

app = FastAPI(title="CDPIA - Diagnostic IA pour PME")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/diagnostic", response_class=HTMLResponse)
async def submit_diagnostic(
    request: Request,
    company_name: str = Form(...),
    contact_email: str = Form(...),
    sector: str = Form(...),
    needs: str = Form(...)
):
    return templates.TemplateResponse(
        request=request, 
        name="success.html", 
        context={"company_name": company_name, "contact_email": contact_email}
    )

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "app": "CDPIA"}
