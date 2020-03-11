"""Add column for ISI violations."""

import numpy as np
import logging
from phy import IPlugin

refractory_period = 1.5  # Spikes closer than this number will be considered to
                         # violate the refractory period.

logger = logging.getLogger('phy')

class ISIViolationsColumn(IPlugin):
    def attach_to_controller(self, controller):
        """Note that this function is called at initialization time, *before* the supervisor is
        created. The `controller.cluster_metrics` items are then passed to the supervisor when
        constructing it."""

        def isiviol(cluster_id):
            t = controller.get_spike_times(cluster_id).data
            violations = 0
            if len(t) >= 2:
                violations = np.count_nonzero(np.diff(t) < refractory_period / 1e3)
                violations = violations / len(t) * 100 # Convert to percentage
            return violations

        # Use this dictionary to define custom cluster metrics.
        # We memcache the function so that cluster metrics are only computed once and saved
        # within the session, and also between sessions (the memcached values are also saved
        # on disk).
        controller.cluster_metrics['ISIviol'] = controller.context.memcache(isiviol)
