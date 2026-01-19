import eventlet
eventlet.monkey_patch()

import os
import sys
from ryu.cmd.manager import main

if __name__ == "__main__":
    os.environ.setdefault("EVENTLET_NO_GREENDNS", "yes")

    if len(sys.argv) == 1:
        sys.argv += [
            "--ofp-tcp-listen-port", "6653",
            "--wsapi-host", "127.0.0.1",
            "--wsapi-port", "8080",
            "src/controller/sdn_security_app.py",
        ]

    main()
