"""Contamination clustering metric"""

import logging
import numpy as np
from phy import IPlugin
from phylib.stats import correlograms

logger = logging.getLogger('phy')


class Contamination(IPlugin):
    def attach_to_controller(self, controller):
        def contamination(cluster_id):
            logger.debug('Compute correlogram of cluster %i.', cluster_id)

            bin_size = 1 / 1000
            window_size = 500
            # st = controller.get_spike_times(cluster_id).data
            # sc = np.ones(len(t), dtype='int64') * cluster_id

            spike_ids = controller.selector.select_spikes(
                [cluster_id], controller.n_spikes_correlograms,
                subset='random')
            st = controller.model.spike_times[spike_ids]
            sc = controller.supervisor.clustering.spike_clusters[spike_ids]
            ccg = correlograms(st, sc,
                               sample_rate=controller.model.sample_rate,
                               cluster_ids=[cluster_id], bin_size=bin_size,
                               window_size=window_size)

            print(np.squeeze(ccg).shape)

            return 0

        # Use this dictionary to define custom cluster metrics.
        # We memcache the function so that cluster metrics are only
        # computed once and saved within the session, and also between
        # sessions (the memcached values are also saved on disk).
        controller.cluster_metrics['cont'] = (
            controller.context.memcache(contamination)
        )

        # # For debugging/testing use this instead
        # controller.cluster_metrics['contamination'] = contamination
