"""
Additional jump options in trace view.
"""

import logging
import numpy as np
from phy import IPlugin, connect
from phy.cluster.views.trace import TraceView as TraceView

logger = logging.getLogger('phy')


class JumpInTrace(IPlugin):

    def attach_to_controller(self, controller):

        @connect
        def on_view_attached(view, gui):
            if isinstance(view, TraceView):

                def _jump_to_spike(delta=+1):
                    """
                    Move within the spikes of any of the selected clusters.
                    """
                    time = view.time  # Current position

                    selected = controller.supervisor.selected
                    spt = np.array([])
                    for sel in selected:
                        spt = np.hstack((spt,
                                         (controller.get_spike_times(sel))))
                    spike_times = np.sort(spt)
                    ind = np.searchsorted(spike_times, time)
                    n = len(spike_times)
                    target = spike_times[(ind + delta) % n]
                    logger.debug('Jump with %+d to one of the spikes from '
                                 'clusters %s. Jumped from %.5f to %.5f.',
                                 delta, ', '.join(map(str, selected)), time,
                                 target)
                    view.go_to(target)

                @view.actions.add(shortcut='shift+alt+pgdown',
                                  name='Jump to next spike')
                def jump_to_next_spike():
                    """
                    Go to next spike from any selected cluster.
                    """
                    _jump_to_spike(+1)

                @view.actions.add(shortcut='shift+alt+pgup',
                                  name='Jump to previous spike')
                def jump_to_prev_spike():
                    """
                    Go to previous spike from any selected cluster.
                    """
                    _jump_to_spike(-1)
