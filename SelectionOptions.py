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


Select the next/previous/newest (non noise) cluster
---------------------------------------------------

Select the cluster with the highest id (among non-noise clusters). This
is useful after performing an action and losing track of the recently
created cluster.


Select all unsorted clusters in current channel
-----------------------------------------------

Select all yet unsorted clusters within the current channel. This is
useful to quickly see all clusters side-by-side.


Select all similar clusters of certain similarity
-------------------------------------------------

Select all non-noise clusters down to a desired similarity threshold or
within a certain range of similarity, depending on whether one or two
arguments are specified. This is useful to see candidates for merging
at a glance.
"""

import numpy as np
from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class SelectionOptions(IPlugin):
    # Safety measure of maximum resulting selections
    max_selections = 50

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
                    logger.debug('Not enough clusters selected.')
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

            def selectnearest(start=None, direction=1):
                """Select the nearest non-noise cluster"""
                ids = controller.supervisor.clustering.cluster_ids
                if isinstance(ids, np.ndarray):
                    ids = ids.tolist()
                assert len(ids) > 0

                # Arrange cluster id list for traversing
                ids = sorted(ids)[::direction]
                if start in ids:
                    ids = ids[ids.index(start)+1:]

                # Traverse in desired direction
                groups = controller.supervisor.get_labels('group')
                for nearest in ids:
                    if groups[nearest] != 'noise':
                        break
                else:
                    return

                if controller.supervisor.selected_clusters == [nearest]:
                    return

                logger.info('Change selection from %s to %i.',
                            ', '.join(map(str,
                                          controller.supervisor.selected)),
                            nearest)
                controller.supervisor.select(nearest)

            @controller.supervisor.actions.add(shortcut='shift+pgup',
                                               name='Select next higher '
                                                    'cluster',
                                               menu='Sele&ct')
            def selectpreviousid():
                """Select the next higher (non-noise) cluster id"""
                sup = controller.supervisor

                # Safety check in case there was no prior selection
                if not sup.selected_clusters:
                    logger.debug('No clusters selected.')
                    return

                sel = max(sup.selected_clusters)
                selectnearest(sel, -1)

            @controller.supervisor.actions.add(shortcut='shift+pgdown',
                                               name='Select next lower '
                                                    'cluster',
                                               menu='Sele&ct')
            def selectnextid():
                """Select the next lower (non-noise) cluster id"""
                sup = controller.supervisor

                # Safety check in case there was no prior selection
                if not sup.selected_clusters:
                    logger.debug('No clusters selected.')
                    return

                sel = max(sup.selected_clusters)
                selectnearest(sel, 1)

            @controller.supervisor.actions.add(shortcut='shift+end',
                                               name='Select newest cluster',
                                               menu='Sele&ct')
            def selectnewest():
                """Select the newest (non noise) cluster"""
                selectnearest(direction=-1)

            @controller.supervisor.actions.add(shortcut='ctrl+shift+a',
                                               name='Select all in channel',
                                               menu='Sele&ct')
            def selectallinchannel():
                """Select all unsorted clusters in current channel"""
                sup = controller.supervisor

                # Safety check in case there was no prior selection
                if not sup.selected_clusters:
                    logger.debug('No clusters selected.')
                    return

                # Obtain the currently selected channel
                channel = set(sup.get_cluster_info(c)['ch']
                              for c in sup.selected_clusters)
                if len(channel) != 1:
                    logger.warn('Error: Selection exceeds one channel')
                    return
                channel = channel.pop()

                # Get all cluster IDs belonging to that channel
                all_clusters = sup.cluster_info
                sel = [c['id'] for c in all_clusters if c['ch'] == channel and
                       c['group'] not in ('noise', 'good')]

                if len(sel) < 1:
                    logger.info('Channel %s fully sorted.', channel)
                    return

                # Safety measure
                if len(sel) > self.max_selections:
                    logger.warn('Capped the number of selections from %i '
                                'to %i.', len(sel), self.max_selections)
                    sel = sel[:self.max_selections]
                    capped = 'the first %i' % self.max_selections
                else:
                    capped = 'all'

                logger.info('Select %s unsorted clusters in channel %s',
                            capped, channel)

                sup.select(sel)

            @controller.supervisor.actions.add(shortcut='ctrl+shift+j',
                                               name='Select similar clusters',
                                               alias='selsim',
                                               menu='Sele&ct',
                                               prompt=True,
                                               prompt_default=lambda: 0.8)
            def Selected_similar_clusters(low, high=1.01):
                """
                Select all similar clusters down to a certain
                similarity (one argument) or within a range (two
                arguments)
                """
                sup = controller.supervisor

                # Safety check in case there was no prior selection
                if not sup.selected_clusters:
                    logger.debug('No clusters selected.')
                    return

                # Only consider one selected cluster
                cid = sup.selected_clusters[0]

                # Verify user input
                if hasattr(low, '__len__') and len(low) == 2:
                    low, high = low

                if not isinstance(low, float) or not isinstance(high, float):
                    logger.warn('Error: Invalid input. One or two floats '
                                'expected')

                # Resort the ranges
                low, high = min(low, high), max(low, high)

                # Verify ranges
                if not (0 <= low <= 1) or high < 0:
                    logger.warn('Error: Invalid input. Values expected '
                                'between [0, 1].')
                    return

                # Obtain all similar clusters
                sel = [s['id'] for s in sup._get_similar_clusters(None, cid)
                       if low <= float(s['similarity']) < high
                       and s['group'] != 'noise']

                if len(sel) < 1:
                    logger.info('No similar clusters found.')
                    return

                # Safety measure
                if len(sel)+1 > self.max_selections:
                    logger.warn('Capped the number of selections from %i '
                                'to %i.', len(sel)+1, self.max_selections)
                    sel = sel[:self.max_selections-1]
                    capped = 'the first %i' % self.max_selections
                else:
                    capped = 'all'

                logger.info('Select %s non-noise clusters with a similarity '
                            'between %g and %g to cluster %i.', capped, low,
                            min(high, 1), cid)

                # Let the TaskLogger take care of making the selections
                sup.task_logger._select_state(([cid], None, sel, None))
                sup.task_logger.process()
