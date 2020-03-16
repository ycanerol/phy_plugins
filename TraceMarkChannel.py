"""
Mark selected channels in trace view
"""

import numpy as np
from phy.cluster.views import TraceView
from phy import IPlugin, connect
from phy.utils.color import selected_cluster_color


class TraceMarkChannel(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, TraceView):
                # Add attribute
                view.ch = []
                view.ch_colors = []

                # Overwrite the label plotting of the view
                def _plot_labels(traces):
                    view.text_visual.reset_batch()
                    for ch in range(view.n_channels):
                        bi = view.channel_y_ranks[ch]
                        ch_label = view.channel_labels[ch]
                        view.text_visual.add_batch_data(
                            pos=[view.data_bounds[0], 0],
                            text=ch_label,
                            anchor=[+1., 0],
                            data_bounds=view.data_bounds,
                            box_index=bi,
                            color=(view.ch_colors[view.ch.index(ch_label)]
                                   if ch_label in view.ch else None)
                        )
                    view.canvas.update_visual(view.text_visual)
                view._plot_labels = _plot_labels

                @connect(sender=controller.supervisor)
                def on_select(sender, cluster_ids=None, **kwargs):
                    if not cluster_ids:
                        view.ch = []
                        view.ch_colors = []
                        return

                    # Get selected channels
                    view.ch = [controller.supervisor.get_cluster_info(c)['ch']
                               for c in cluster_ids]
                    view.ch, c_ids = np.unique(view.ch, return_index=True)
                    view.ch = view.ch.tolist()

                    # Get cluster colors
                    view.ch_colors = [selected_cluster_color(i, alpha=1)
                                      for i in range(len(cluster_ids))]
                    view.ch_colors = np.asarray(view.ch_colors)[c_ids]

                    # Update highlighting
                    view._plot_labels(None)
