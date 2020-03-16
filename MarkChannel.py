"""
Highlight all clusters in the same channel
"""

import numpy as np
from phy import IPlugin, connect
from phy.cluster.supervisor import ClusterView
from phy.utils.color import selected_cluster_color


class MarkChannel(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @connect(sender=controller.supervisor)
            def on_select(sender, cluster_ids=None, **kwargs):
                view = gui.get_view(ClusterView)

                if not cluster_ids:
                    return

                # Get selected channels
                channels = [sender.get_cluster_info(c)['ch']
                            for c in cluster_ids]
                channels, c_ids = np.unique(channels, return_index=True)
                channels = channels.tolist()

                # Get cluster colors
                colors = [selected_cluster_color(i, alpha=1)
                          for i in range(len(cluster_ids))]
                colors = (np.asarray(colors)[c_ids] * 255).astype(int)[:, :3]
                colors = [('rgba(' + ', '.join(map(str, c)) + ', 0.2)')
                          for c in colors]

                clust = dict()
                for c in sender.clustering.cluster_ids:
                    ch = sender.get_cluster_info(c)['ch']
                    if ch in channels:
                        clust[str(c)] = colors[channels.index(ch)]

                js = """
                    var ll = """ + str(clust) + """;
                    var itms = document.getElementsByTagName("tr");
                    for (var i = 0; i < itms.length; i++) {
                        var c_id = itms[i].getAttribute('data-_id');
                        if (Object.keys(ll).indexOf(c_id) >= 0) {
                            itms[i].style.background = ll[c_id];
                        } else {
                            itms[i].style.background = '';
                        }
                    }
                """
                view.eval_js(js)
