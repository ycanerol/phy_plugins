"""
Reverse the cluster selection

The order of the selection (evident by the coloring of the selection) is
reversed. This is especially useful for finding the first selected
cluster in the trace view when one of the clusters has few spikes.

Both selections from the cluster view and the similarity view are
considered.

Triggering the action twice results in the original selection. If
there were more selections than one cluster view - similarity view pair,
all selections will be moved to cluster view and no longer in the
similarity view.
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
                sup = controller.supervisor

                if len(sup.selected) < 2:
                    return

                if (len(sup.selected) == 2
                        and len(sup.selected_clusters) == 1
                        and len(sup.selected_similar) == 1):
                    # Switch cluster and similarity selection
                    state = (sup.selected_similar, None,
                             sup.selected_clusters, None)
                else:
                    # Move the selection to the cluster view only
                    state = (sup.selected[::-1], None, None, None)

                logger.info('Reverse selection of clusters from %s to %s.',
                            ', '.join(map(str, sup.selected)),
                            ', '.join(map(str, sup.selected[::-1])))

                # Let the TaskLogger take care of making the selections
                sup.task_logger._select_state(state)
                sup.task_logger.process()
