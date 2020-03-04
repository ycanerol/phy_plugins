"""
Additional selection options
============================

Reverse the cluster selection
-----------------------------

The order of the selection (evident by the coloring of the selection) is
reversed. This is especially useful for finding the first selected
cluster in the trace view when one of the clusters has few spikes.

Both selections from the cluster view and the similarity view are
considered.

Triggering the action twice results in the original selection. If
there were more selections than one cluster view - similarity view pair,
all selections will be moved to cluster view and no longer in the
similarity view.


Select the newest (non noise) cluster
-------------------------------------

Select the cluster with the highest id (among non-noise clusters). This
is useful after performing an action and losing track of the recently
created cluster.


Select all unsorted clusters in current channel
-----------------------------------------------

Select all yet unsorted clusters within the current channel. This is
useful to quickly see all clusters side-by-side.
"""

import numpy as np
from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class SelectionOptions(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @controller.supervisor.actions.add(shortcut='alt+y',
                                               name='Reverse selection',
                                               menu='Sele&ct')
            def reverseselection():
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

            @controller.supervisor.actions.add(shortcut='shift+pgdown',
                                               name='Select newest cluster',
                                               menu='Sele&ct')
            def selectnewest():
                """Select the newest (non noise) cluster"""
                sup = controller.supervisor

                # Find the highest non-noise cluster
                groups = sup.get_labels('group')
                ids = sup.clustering.cluster_ids
                if isinstance(ids, np.ndarray):
                    ids = ids.tolist()
                highest = max(ids)
                while len(ids) > 0 and groups[highest] == 'noise':
                    ids.remove(highest)
                    highest = max(ids)

                if sup.selected == [highest] or len(ids) < 1:
                    return

                logger.info('Change selection from %s to %i.',
                            ', '.join(map(str, sup.selected)), highest)

                sup.select(highest)

            @controller.supervisor.actions.add(shortcut='ctrl+shift+a',
                                               name='Select all in channel',
                                               menu='Sele&ct')
            def selectallinchannel():
                """Select all unsorted clusters in current channel"""
                sup = controller.supervisor

                # Obtain the currently selected channel
                channel = set(sup.get_cluster_info(c)['ch']
                              for c in sup.selected_clusters)
                if len(channel) != 1:
                    logger.warn("Error: Selection exceeds one channel")
                    return
                channel = channel.pop()

                # Get all cluster IDs belonging to that channel
                all_clusters = sup.cluster_info
                sel = [c['id'] for c in all_clusters if c['ch'] == channel and
                       c['group'] not in ('noise', 'good')]

                if len(sel) < 1:
                    logger.info("Channel %s fully sorted.", channel)
                    return

                logger.info('Change selection from %s to channel %s (%s).',
                            ', '.join(map(str, sup.selected)), channel,
                            ', '.join(map(str, sel)))

                sup.select(sel)
