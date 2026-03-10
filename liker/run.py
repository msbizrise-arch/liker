# noinspection PyUnresolvedReferences
import inject
from tengi import App

from liker.setup.dependencies import bind_app_dependencies
from liker.setup.daemons import create_daemon_instances


import os
from flask import Flask
from threading import Thread
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Ab original imports chalenge, jaise from liker.setup import logs

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Agar polling line if __name__ == '__main__': ke andar hai, toh yahan add
if __name__ == '__main__':
    # Flask background thread mein start
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Ab original polling start line daal (jo error de rahi thi, usko uncomment/restore kar)
    # Example agar tengi/aiogram style hai:
    # dp.run_polling()   # ya jo bhi original polling call hai
    # Ya agar bot.polling():
    # bot.polling(none_stop=True, interval=0, timeout=20)


@inject.autoparams()
def main():
    inject.configure(bind_app_dependencies)
    create_daemon_instances()

    app = inject.instance(App)
    app.run()


if __name__ == '__main__':
    main()
