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
        def on_gui_ready(sender, gui):

            trace_view = gui.get_view(TraceView)
            go_to = trace_view.go_to

            def _jump_to_spike(delta=+1):
                """
                Move within the spikes of any of the selected clusters.
                """
                time = trace_view.time  # Current position

                selected = controller.supervisor.selected
                spt = []
                for sel in selected:
                    spt.extend(list(controller.get_spike_times(sel)))
                spike_times = sorted(spt)
                ind = np.searchsorted(spike_times, time)
                n = len(spike_times)
                target = spike_times[(ind + delta) % n]
                logger.debug(f"Jump with {delta} to one of the spikes from"
                             f" clusters {selected}. Jumped from {time:.5f} "
                             f"to {target:.5f}.")
                go_to(target)

            @controller.supervisor.actions.add(shortcut='shift+alt+pgdown',
                                               name='Next spike',
                                               menu='&View',
                                               #submenu='TraceView',
                                               )
            def jump_to_next_spike():
                """
                Go to next spike from any selected cluster.
                """
                _jump_to_spike(+1)

            @controller.supervisor.actions.add(shortcut='shift+alt+pgup',
                                               name='Previous spike',
                                               menu='&View',
                                               #submenu='TraceView',
                                               )
            def jump_to_prev_spike():
                """
                Go to previous spike from any selected cluster.
                """
                _jump_to_spike(-1)
