"""
Highlight all clusters in the same channel
"""

import numpy as np
from phy import IPlugin, connect
from phy.cluster.supervisor import ClusterView
from phy.utils.color import selected_cluster_color
import logging

logger = logging.getLogger('phy')


class MarkChannel(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @connect(sender=controller.supervisor)
            def on_select(sender, cluster_ids=None, **kwargs):
                view = gui.get_view(ClusterView)

                # Get selected channels
                channels = [sender.get_cluster_info(c)['ch']
                            for c in cluster_ids]
                channels, c_ids = np.unique(channels, return_index=True)
                channels = channels.tolist()

                # Get cluster colors
                colors = [selected_cluster_color(i, alpha=1)
                          for i in range(len(cluster_ids))]
                colors = (np.asarray(colors)[c_ids] * 255).astype(int)
                colors = [('rgba(' + ', '.join(map(str, c[:3])) + ', 0.2)')
                          for c in colors]

                clust = dict()
                for c in sender.clustering.cluster_ids:
                    ch = sender.get_cluster_info(c)['ch']
                    if ch in channels:
                        clust[str(c)] = colors[channels.index(ch)]

                js = """
                    var ll = """ + str(clust) + """;
                    var itms = document.getElementsByTagName("tr");
                    var chng = []
                    for (var i = 0; i < itms.length; i++) {
                        var c_id = itms[i].getAttribute('data-_id');

                        // New clusters do not have this attribute
                        if (!c_id) {
                            c_id = itms[i].getElementsByClassName('id')
                            if (c_id.length) {
                                c_id = c_id[0].innerHTML;
                            } else {
                                continue;
                            }
                        };

                        if (Object.keys(ll).indexOf(c_id) >= 0) {
                            itms[i].style.background = ll[c_id];
                            chng.push(c_id);
                        } else {
                            itms[i].style.background = '';
                        }
                    }

                    // Report highlighted clusters to callback function
                    chng
                """

                def report(obj):
                    logger.debug('Highlighted clusters %s.',
                                 ', '.join(obj) if len(obj) > 0 else 'none')

                view.eval_js(js, callback=report)
