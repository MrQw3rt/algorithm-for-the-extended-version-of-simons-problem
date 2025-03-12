import logging
import sys

log = logging.getLogger('SimonSolver')
log.setLevel(logging.INFO)

stream = logging.StreamHandler(stream=sys.stdout)
log.addHandler(stream)

fmt = logging.Formatter("%(levelname)s:%(name)s:%(lineno)s: %(message)s")
stream.setFormatter(fmt)

