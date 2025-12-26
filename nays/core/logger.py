from colorama import Fore, Style, init
import logging

def setupLogger(name: str = "nays") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()

        class ColorFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': Fore.MAGENTA,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.MAGENTA
            }

            def format(self, record):
                color = self.COLORS.get(record.levelname, "")
                levelname_colored = f"{color}{record.levelname}{Style.RESET_ALL}"
                record.levelname = levelname_colored
                return super().format(record)

        formatter = ColorFormatter(
            fmt='%(asctime)s    [%(name)s] [%(levelname)s]: %(message)s',
            datefmt='%d-%m-%Y    %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger