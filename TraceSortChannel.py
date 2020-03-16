"""
Sort the channels in trace view
"""

import numpy as np
from phy.cluster.views import TraceView
from phy import IPlugin, connect


class TraceSortChannel(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, TraceView):
                # Update channel order
                idx = np.argsort(view.channel_y_ranks)
                view.channel_y_ranks = view.channel_y_ranks[idx]

                # Update drawing of traces
                _traces = view.traces  # Backup of original function

                def _get_traces(interval):
                    tr = _traces(interval)
                    # tr.data = tr.data[:, idx]  # Already sorted?
                    for wv in tr.waveforms:
                        sort_i = np.argsort(wv.channel_ids)
                        wv['data'] = wv['data'][:, sort_i]
                        wv['channel_ids'] = wv['channel_ids'][sort_i]
                    return tr
                view.traces = _get_traces
