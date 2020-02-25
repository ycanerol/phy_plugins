"""Remove unneccessary columns for curating MEA data"""

from phy import IPlugin, connect


class MEAColumns(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_controller_ready(sender):
            columns_to_remove = ['sh', 'depth', 'amp']
            for col in columns_to_remove:
                controller.supervisor.columns.remove(col)

