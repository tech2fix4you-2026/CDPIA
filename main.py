import os
import uuid
import aiosmtplib
from email.message import EmailMessage
from fastapi import FastAPI, Request, Form, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "contact@humans-and-ai.ca")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

app = FastAPI(title="CDPIA - Bibliothèque IA")
templates = Jinja2Templates(directory="templates")

BASE_DOCS = "Documents"
DIR_DEPART = os.path.join(BASE_DOCS, "Bibliothèque de départ")
DIR_CONVERTIS = os.path.join(BASE_DOCS, "Bibliothèque clients convertis")

async def envoyer_acces_par_courriel(destinataire: str, nom_complet: str, token: str):
    if not SMTP_PASSWORD:
        print("[ALERTE] Envoi annulé: SMTP_PASSWORD non configuré.")
        return

    lien_acces = f"https://humans-and-ai.ca/cdpia?token={token}"

    msg = EmailMessage()
    msg['Subject'] = "Vos accès : Bibliothèque de départ CDPIA"
    msg['From'] = "demande@humans-and-ai.ca"
    msg['To'] = destinataire

    contenu_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <p>Bonjour {nom_complet},</p>
            <p>Merci pour votre intérêt envers le Centre de Déploiement Pragmatique de l'IA (CDPIA).</p>
            <p>Voici votre lien d'accès à la <strong>Bibliothèque de départ</strong> :</p>
            <p style="margin: 20px 0;">
                <a href="{lien_acces}" style="background-color: #4f46e5; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    Accéder à mes documents
                </a>
            </p>
            <p>Si le bouton ne s'affiche pas, collez ce lien dans votre navigateur :<br>
            <a href="{lien_acces}" style="color: #4f46e5;">{lien_acces}</a></p>
            <p>Bonne consultation,</p>
            <p><strong>L'équipe Humans and AI</strong></p>
        </body>
    </html>
    """
    msg.set_content("Veuillez activer l'affichage HTML pour lire ce courriel.")
    msg.add_alternative(contenu_html, subtype='html')

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
        print(f"[Succès] Accès expédié par courriel à {destinataire}")
    except Exception as e:
        print(f"[Erreur SMTP] Échec lors de l'envoi à {destinataire}: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/cdpia", response_class=HTMLResponse)
async def read_cdpia(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/request-access", response_class=HTMLResponse)
async def request_access(
    request: Request,
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...)
):
    nom_complet = f"{first_name} {last_name}".strip()
    token_prospect = str(uuid.uuid4())

    # Déclenche l'envoi automatisé depuis demande@humans-and-ai.ca
    background_tasks.add_task(envoyer_acces_par_courriel, email, nom_complet, token_prospect)

    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={"first_name": first_name, "last_name": last_name, "email": email}
    )

@app.get("/telecharger/depart/{filename}")
async def get_depart_file(filename: str, token: str = Query(...)):
    if not token or len(token) < 5:
        raise HTTPException(status_code=403, detail="Lien expiré ou non valide")
    file_path = os.path.join(DIR_DEPART, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document introuvable")
    return FileResponse(file_path, filename=filename)

@app.get("/telecharger/client/{filename}")
async def get_client_file(filename: str, client_key: str = Query(...)):
    if not client_key or len(client_key) < 10:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    file_path = os.path.join(DIR_CONVERTIS, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document introuvable")
    return FileResponse(file_path, filename=filename)

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "app": "CDPIA"}
