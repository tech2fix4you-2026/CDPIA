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
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "guy@next-ai.ca")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
NOTIFICATION_RECIPIENT = os.getenv("NOTIFICATION_RECIPIENT", "guy@next-ai.ca")

# Détection automatique du mode TLS selon le port
USE_TLS = (SMTP_PORT == 465)
START_TLS = (SMTP_PORT == 587)

app = FastAPI(title="CDPIA - Bibliothèque IA")
templates = Jinja2Templates(directory="templates")

BASE_DOCS = "Documents"
DIR_DEPART = os.path.join(BASE_DOCS, "Bibliothèque de départ")
DIR_CONVERTIS = os.path.join(BASE_DOCS, "Bibliothèque clients convertis")

async def dispatcher_courriels(destinataire: str, nom_complet: str, token: str):
    if not SMTP_PASSWORD:
        print("[ALERTE] SMTP_PASSWORD manquant.")
        return

    lien_acces = f"https://humans-and-ai.ca/cdpia?token={token}"

    # 1. Message pour le prospect
    msg_client = EmailMessage()
    msg_client['Subject'] = "Vos accès : Bibliothèque de départ CDPIA"
    msg_client['From'] = "demande@humans-and-ai.ca"
    msg_client['To'] = destinataire

    html_client = f"""
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
            <p>Lien direct : <a href="{lien_acces}" style="color: #4f46e5;">{lien_acces}</a></p>
            <p>Bonne consultation,</p>
            <p><strong>L'équipe Humans and AI</strong></p>
        </body>
    </html>
    """
    msg_client.set_content("Veuillez activer l'affichage HTML pour lire ce courriel.")
    msg_client.add_alternative(html_client, subtype='html')

    # 2. Notification administrateur
    msg_admin = EmailMessage()
    msg_admin['Subject'] = f"[Nouveau Prospect CDPIA] {nom_complet}"
    msg_admin['From'] = "demande@humans-and-ai.ca"
    msg_admin['To'] = NOTIFICATION_RECIPIENT

    html_admin = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
            <h3>Nouvelle demande d'accès - Bibliothèque de départ</h3>
            <ul>
                <li><strong>Nom :</strong> {nom_complet}</li>
                <li><strong>Courriel :</strong> {destinataire}</li>
                <li><strong>Jeton généré :</strong> {token}</li>
            </ul>
        </body>
    </html>
    """
    msg_admin.set_content(f"Nouveau prospect : {nom_complet} ({destinataire})")
    msg_admin.add_alternative(html_admin, subtype='html')

    try:
        await aiosmtplib.send(
            msg_client,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=USE_TLS,
            start_tls=START_TLS,
            username=SMTP_USER,
            password=SMTP_PASSWORD
        )
        print(f"[Succès] Accès expédié au prospect : {destinataire}")

        await aiosmtplib.send(
            msg_admin,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=USE_TLS,
            start_tls=START_TLS,
            username=SMTP_USER,
            password=SMTP_PASSWORD
        )
        print(f"[Succès] Notification admin envoyée à : {NOTIFICATION_RECIPIENT}")
    except Exception as e:
        print(f"[Erreur SMTP] Échec d'envoi : {e}")

@app.get("/", response_class=HTMLResponse)
@app.get("/cdpia", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/request-access", response_class=HTMLResponse)
@app.post("/cdpia/request-access", response_class=HTMLResponse)
async def request_access(
    request: Request,
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...)
):
    nom_complet = f"{first_name} {last_name}".strip()
    token_prospect = str(uuid.uuid4())
    background_tasks.add_task(dispatcher_courriels, email, nom_complet, token_prospect)

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
