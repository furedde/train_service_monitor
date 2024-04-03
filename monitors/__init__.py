from .odakyu import OdakyuMonitor
from .soutetsu import SoutetsuMonitor
from .metro import MetroMonitor

MONITORS = [OdakyuMonitor(), SoutetsuMonitor(), MetroMonitor('千代田線')]
