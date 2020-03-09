"""Remove unneccessary columns for curating MEA data"""

from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class MEAColumns(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_controller_ready(sender):
            columns_to_remove = ['sh', 'depth', 'Amplitude']
            for col in columns_to_remove:
                if col in controller.supervisor.columns:
                    logger.debug('Remove column `%s`.', col)
                    controller.supervisor.columns.remove(col)
