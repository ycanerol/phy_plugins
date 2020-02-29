"""
Reverse the cluster selection

The order of the selection (evident by the coloring of the selection) is
reversed. This is especially useful for finding the first selected
cluster in the trace view.

Both selections from the cluster view and the similarity view are
considered. Selections from the similarity view are moved to the cluster
view on reversal of the order.

Triggering the action twice results in the original selection with the
difference of all selections are in the cluster view and no longer in
the similarity view.
"""

from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class ReverseSelection(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @controller.supervisor.actions.add(alias='rev', shortcut='alt+y')
            def Reverse_selection():
                """Reverse the current cluster selection order"""
                cid = controller.supervisor.selected
                controller.supervisor.unselect_similar()
                controller.supervisor.select(cid[::-1])

                logger.info('Reverse selection of clusters from %s to %s.',
                            ', '.join(map(str, cid)),
                            ', '.join(map(str, cid[::-1])))
