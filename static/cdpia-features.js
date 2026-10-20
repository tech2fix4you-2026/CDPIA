(() => {
  // 1. BANNIÈRE D'INSTALLATION MOBILE (PWA)
  let deferredPrompt = null;
  const isIos = /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
  const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

  function injectInstallPrompt() {
    if (isInStandaloneMode || sessionStorage.getItem('cdpia_prompt_dismissed')) return;

    const banner = document.createElement('div');
    banner.id = 'cdpia-pwa-banner';
    banner.style.cssText = `
      position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
      width: 90%; max-width: 420px; background: #111; color: #fff;
      padding: 16px 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      z-index: 99999; font-family: system-ui, -apple-system, sans-serif; display: flex;
      flex-direction: column; gap: 10px; border: 1px solid #333;
    `;

    banner.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <strong style="font-size: 15px; display:block;">Installer Humans & AI ?</strong>
          <span style="font-size: 12px; color: #aaa;">Accédez directement à vos ressources depuis votre écran d'accueil.</span>
        </div>
        <button id="pwa-close" style="background:none; border:none; color:#888; font-size:18px; cursor:pointer; line-height:1;">&times;</button>
      </div>
      <div style="display:flex; gap: 8px; margin-top: 4px;">
        <button id="pwa-install-btn" style="flex:1; background:#fff; color:#000; font-weight:600; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-size:13px;">
          Installer
        </button>
        <button id="pwa-later-btn" style="background:#222; color:#ccc; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-size:13px;">
          Plus tard
        </button>
      </div>
      <div id="pwa-ios-instructions" style="display:none; font-size:11px; color:#ffcc00; margin-top:4px;">
        Sur iPhone : appuyez sur le bouton de partage <span style="font-size:14px;">⎋</span> puis sur <strong>« Sur l'écran d'accueil »</strong>.
      </div>
    `;

    document.body.appendChild(banner);

    const close = () => { banner.remove(); sessionStorage.setItem('cdpia_prompt_dismissed', 'true'); };
    document.getElementById('pwa-close').addEventListener('click', close);
    document.getElementById('pwa-later-btn').addEventListener('click', close);
    document.getElementById('pwa-install-btn').addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') close();
        deferredPrompt = null;
      } else if (isIos) {
        document.getElementById('pwa-ios-instructions').style.display = 'block';
      } else {
        alert("Pour installer : ouvrez le menu de votre navigateur (⋮) et sélectionnez « Installer l'application ».");
      }
    });
  }

  window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; injectInstallPrompt(); });
  if (isIos && !isInStandaloneMode) { window.addEventListener('load', injectInstallPrompt); }

  // 2. LOGIQUE DU FORMULAIRE "BIBLIOTHÈQUE DE DÉPART"
  document.addEventListener('DOMContentLoaded', () => {
    const formContainer = document.querySelector('.cdpia-form-wrapper') || document.querySelector('form')?.parentElement;
    if (formContainer) {
      formContainer.innerHTML = `
        <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #eaeaea; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
          <h3 style="margin-top:0; font-size: 18px; color: #111;">Accès : Bibliothèque de départ</h3>
          <p style="font-size: 13px; color: #666; margin-bottom: 15px;">Le questionnaire de statut, les guides d'introduction et l'évaluation de maturité.</p>
          
          <form id="cdpia-access-form" style="display:flex; flex-direction:column; gap:12px;">
            <input type="text" name="hp_field" style="display:none;" tabindex="-1" autocomplete="off">
            
            <div>
              <label style="display:block; font-size:12px; font-weight:600; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.5px;">Nom complet</label>
              <input type="text" name="fullname" required style="width:100%; padding:10px; border-radius:6px; border:1px solid #ccc; font-size:14px; box-sizing:border-box;">
            </div>
            
            <div>
              <label style="display:block; font-size:12px; font-weight:600; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.5px;">Courriel professionnel</label>
              <input type="email" name="email" required style="width:100%; padding:10px; border-radius:6px; border:1px solid #ccc; font-size:14px; box-sizing:border-box;">
            </div>

            <div style="display:flex; align-items:flex-start; gap:8px;">
              <input type="checkbox" id="lcap_consent" required style="margin-top:3px;">
              <label for="lcap_consent" style="font-size:11px; color:#555; line-height:1.4;">
                J'accepte de recevoir mon accès et les communications de Humans and AI. Retrait possible à tout moment (LCAP).
              </label>
            </div>

            <button type="submit" style="background:#000; color:#fff; padding:12px; border:none; border-radius:6px; font-weight:600; cursor:pointer; font-size:14px; margin-top:5px; transition: background 0.3s;">
              Obtenir ma bibliothèque de départ
            </button>
          </form>

          <div id="cdpia-confirmation" style="display:none; padding:15px; background:#f4f9f4; border:1px solid #b7e1cd; border-radius:6px; color:#0f5132; font-size:13px; line-height:1.5;">
            <strong>Demande validée ! 🚀</strong><br><br>
            Vos accès à la <em>Bibliothèque de départ</em> viennent d'être générés. Vérifiez votre boîte de réception (incluant les indésirables). Le courriel provient de <strong>demande@humans-and-ai.ca</strong>.
          </div>
        </div>
      `;

      const form = document.getElementById('cdpia-access-form');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = new FormData(form);
        if (data.get('hp_field')) return; // Bloqueur robot honeypot

        // Remplacement par l'état succès
        form.style.display = 'none';
        document.getElementById('cdpia-confirmation').style.display = 'block';

        // --- C'EST ICI QUE ÇA ENVOIE LES DONNÉES À TON PYTHON (main.py) ---
        try {
          await fetch('/api/demande-acces', {
            method: 'POST',
            body: data
          });
        } catch (error) {
          console.error('Erreur lors de la requête backend:', error);
        }
      });
    }

    // 3. VÉRIFICATION DU TOKEN (Pour la page où est hébergée la bibliothèque)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const privateLibraryArea = document.getElementById('private-library-content');

    if (privateLibraryArea) {
      if (!token) {
        privateLibraryArea.innerHTML = `
          <div style="text-align:center; padding:40px 20px; border:1px dashed #ccc; border-radius:8px;">
            <h3>Espace protégé</h3>
            <p style="color:#666; font-size:14px;">La Bibliothèque de départ est accessible uniquement sur demande. Veuillez remplir le formulaire pour recevoir votre lien.</p>
          </div>
        `;
      }
    }
  });
})();
