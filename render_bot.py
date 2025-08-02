#!/usr/bin/env python3
"""
Version optimisée pour déploiement Render.com
Bot Telegram standalone pour fonctionnement 24h/7
"""

import os
import sys
import time
import signal
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify

# Importer les modules du bot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from telegram_standalone import main as run_telegram_bot
    from config import config
except ImportError as e:
    print(f"Erreur import: {e}")
    # Fallback pour Render
    def run_telegram_bot():
        pass

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app pour health check Render
app = Flask(__name__)

class RenderBotManager:
    """Gestionnaire de bot optimisé pour Render.com"""
    
    def __init__(self):
        self.running = True
        self.bot_thread = None
        self.start_time = datetime.now()
        
        # Configuration Render
        self.port = int(os.environ.get('PORT', 10000))
        
        logger.info("🚀 Démarrage bot pour Render.com...")
        
        # Gestionnaires de signaux
        signal.signal(signal.SIGTERM, self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup)
    
    def _cleanup(self, signum=None, frame=None):
        """Nettoyage propre"""
        logger.info("Arrêt propre du bot...")
        self.running = False
        sys.exit(0)
    
    def start_bot_thread(self):
        """Démarre le bot Telegram en thread séparé"""
        try:
            logger.info("Démarrage thread bot Telegram...")
            self.bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
            self.bot_thread.start()
            logger.info("✅ Bot Telegram démarré en arrière-plan")
        except Exception as e:
            logger.error(f"Erreur démarrage bot: {e}")
    
    def start_web_server(self):
        """Démarre le serveur web Flask pour health checks"""
        logger.info(f"Démarrage serveur web sur port {self.port}...")
        app.run(host='0.0.0.0', port=self.port, debug=False)

# Instance globale
bot_manager = RenderBotManager()

@app.route('/health')
def health_check():
    """Health check pour Render.com"""
    uptime = datetime.now() - bot_manager.start_time
    return jsonify({
        'status': 'healthy',
        'uptime_seconds': uptime.total_seconds(),
        'bot_active': bot_manager.bot_thread.is_alive() if bot_manager.bot_thread else False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def root():
    """Page racine"""
    return jsonify({
        'service': 'AVAX Token Scanner Bot',
        'status': 'running',
        'uptime_seconds': (datetime.now() - bot_manager.start_time).total_seconds()
    })

def main():
    """Point d'entrée principal"""
    logger.info("=" * 50)
    logger.info("🤖 AVAX Token Scanner Bot - Version Render.com")
    logger.info("=" * 50)
    
    # Vérifier les variables d'environnement critiques
    if not os.environ.get('BOT_TOKEN'):
        logger.error("❌ BOT_TOKEN manquant")
        logger.info("Ajoutez BOT_TOKEN dans les variables d'environnement Render")
        # Continuer quand même pour que le service démarre
    
    if not os.environ.get('CHAT_ID'):
        logger.error("❌ CHAT_ID manquant")
        logger.info("Ajoutez CHAT_ID dans les variables d'environnement Render")
    
    # Démarrer le bot en arrière-plan
    bot_manager.start_bot_thread()
    
    # Démarrer le serveur web (bloquant)
    logger.info("🌐 Démarrage serveur web pour health checks...")
    bot_manager.start_web_server()

if __name__ == "__main__":
    main()