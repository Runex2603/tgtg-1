import logging
import subprocess
from typing import Union

from tgtg_scanner.models import Config, Favorites, Item, Reservations
from tgtg_scanner.models.errors import (MaskConfigurationError,
                                        ScriptConfigurationError)
from tgtg_scanner.models.reservations import Reservation
from tgtg_scanner.notifiers import Notifier

log = logging.getLogger('tgtg')


class Script(Notifier):
    """Notifier for the script output"""

    def __init__(self, config: Config, reservations: Reservations,
                 favorites: Favorites):
        super().__init__(config, reservations, favorites)
        self.enabled = config.script.get("enabled", False)
        self.command = config.script.get("command")
        self.cron = config.script.get("cron")

        if self.enabled and (not self.command):
            raise ScriptConfigurationError()
        if self.enabled:
            try:
                Item.check_mask(self.command)
            except MaskConfigurationError as exc:
                raise ScriptConfigurationError(exc.message) from exc

    def _send(self, item: Union[Item, Reservation]) -> None:
        if isinstance(item, Item):
            args = [item.unmask(arg) for arg in self.command.split()]
            subprocess.Popen(args)

    def __repr__(self) -> str:
        return f"Shell script: {self.command}"
