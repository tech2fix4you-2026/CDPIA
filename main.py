import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

app = FastAPI(title="CDPIA - Diagnostic IA pour PME")

templates = Jinja2Templates(directory="templates")

class DiagnosticInput(BaseModel):
    company_name: str
    contact_email: EmailStr
    sector: str
    needs: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Correction de la signature TemplateResponse
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/diagnostic")
async def submit_diagnostic(
    company_name: str = Form(...),
    contact_email: str = Form(...),
    sector: str = Form(...),
    needs: str = Form(...)
):
    return {
        "status": "success",
        "message": f"Diagnostic initié pour {company_name}",
        "recipient": contact_email,
        "details": {"sector": sector, "needs": needs}
    }

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "app": "CDPIA"}
