"""
Mark selected channels in trace view
"""

from phy.cluster.views import TraceView
from phy import IPlugin, connect


class TraceMarkChannel(IPlugin):
    # Highlight color
    text_color = (1, 0, 0, 1)

    def attach_to_controller(self, controller):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, TraceView):
                @connect(sender=controller.supervisor)
                def on_select(sender, cluster_ids=None, **kwargs):
                    if not cluster_ids:
                        return

                    # Get selected channels
                    channels = set(
                        int(controller.supervisor.get_cluster_info(c)['ch'])
                        for c in cluster_ids
                    )

                    # Mimic _plot_labels
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
                            color=self.text_color if ch in channels else None
                        )
                    view.canvas.update_visual(view.text_visual)
