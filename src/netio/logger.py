import logging
logging.EVENT = 60
logging.addLevelName(60, "EVENT")

def event(self, message, *args, **kws):
    if self.isEnabledFor(logging.EVENT):
        self._log(logging.EVENT, message, args, **kws)
logging.Logger.event = event

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message: str, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'EVENT': BLUE
}

class ColoredFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            return COLOR_SEQ % (30 + COLORS[levelname]) + logging.Formatter.format(self, record) + RESET_SEQ
        return logging.Formatter.format(self, record)
    
formatter = ColoredFormatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

clientLogger = logging.getLogger("CLIENT")
serverLogger = logging.getLogger("SERVER")

logging.basicConfig(filename='network.log', level=logging.DEBUG)
logging.getLogger().addHandler(handler)