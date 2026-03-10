import os
import sys
from threading import Thread

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import inject
from flask import Flask
from tengi import App

from liker.setup.dependencies import bind_app_dependencies
from liker.setup.daemons import create_daemon_instances

# Flask app for Render port binding
flask_app = Flask(__name__)

@flask_app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


@inject.autoparams()
def main():
    inject.configure(bind_app_dependencies)
    create_daemon_instances()

    # ── Fix: Telegram auto-converts "--" to "—" (em dash), convert it back ──
    from tengi import TelegramBot
    bot = inject.instance(TelegramBot).bot

    @bot.middleware_handler(update_types=['message'])
    def fix_em_dash(bot_instance, message):
        if message.text:
            # em dash (—) and en dash (–) → double dash (--)
            message.text = message.text.replace('\u2014', '--').replace('\u2013', '--')

    # Flask ko background thread mein start karo
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Bot ko main thread mein run karo
    app = inject.instance(App)
    app.run()


if __name__ == '__main__':
    main()
