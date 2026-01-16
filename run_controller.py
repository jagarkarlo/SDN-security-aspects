import eventlet
eventlet.monkey_patch()

from ryu.cmd.manager import main

if __name__ == "__main__":
    main()
