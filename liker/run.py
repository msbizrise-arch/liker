# run.py ke end pe, before polling start line
import os
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK'

# Flask ko thread mein chalao taaki polling block na ho
# (simple way: separate thread)
if __name__ == '__main__':
    # Pehle Flask start in background
    from threading import Thread
    flask_thread = Thread(target=app.run, kwargs={
        'host': '0.0.0.0',
        'port': int(os.environ.get('PORT', 10000)),
        'debug': False,
        'use_reloader': False
    })
    flask_thread.daemon = True
    flask_thread.start()

    # Ab original polling start kar
    executor.start_polling(dp)   # ya jo bhi polling line hai, usko yahan rakh
    # Agar asyncio based hai to: asyncio.run(main())

# noinspection PyUnresolvedReferences
from liker.setup import logs  # has import side effect
import inject
from tengi import App

from liker.setup.dependencies import bind_app_dependencies
from liker.setup.daemons import create_daemon_instances


@inject.autoparams()
def main():
    inject.configure(bind_app_dependencies)
    create_daemon_instances()

    app = inject.instance(App)
    app.run()


if __name__ == '__main__':
    main()
