"""Remove spikes with low interspike interval"""

from phy import IPlugin, connect
import numpy as np
import logging

logger = logging.getLogger('phy')


class SplitShortISI(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @controller.supervisor.actions.add(shortcut='ctrl+alt+i',
                                               name='Visualize short ISI',
                                               alias='isi')
            def VisualizeShortISI():
                """
                Split all spikes with an interspike interval of less
                than 1.5 ms into a separate cluster.
                THIS IS FOR VISUALIZATION ONLY, it will show you where
                potential noise spikes may be located. Re-merge the
                clusters again afterwards and cut the cluster with
                another method!
                """

                logger.info('Detecting spikes with ISI less than 1.5 ms')

                # Selected clusters across cluster and similarity views
                cluster_ids = controller.supervisor.selected

                # Get amplitudes using the same controller method as
                # what the amplitude view is using.
                # Note that we need load_all=True to load all spikes
                # from the selected clusters, instead of just the
                # selection of them chosen for display
                bunchs = controller._amplitude_getter(cluster_ids,
                                                      name='template',
                                                      load_all=True)

                # Spike ids and corresponding spike template amplitudes
                # NOTE: we only consider the first selected cluster
                spike_ids = bunchs[0].spike_ids
                spike_times = controller.model.spike_times[spike_ids]
                dspike_times = np.diff(spike_times)

                labels = np.ones(len(dspike_times), 'int64')
                labels[dspike_times < .0015] = 2
                # Include last spike to match with len spike_ids
                labels = np.append(labels, 1)

                # # Perform the clustering algorithm, which returns an
                # # integer for each sub-cluster
                # labels = k_means(y.reshape((-1, 1)))

                assert spike_ids.shape == labels.shape

                # We split according to the labels.
                controller.supervisor.actions.split(spike_ids, labels)
                num = np.sum(np.asarray(labels) == 2)
                logger.info('Removed %i spikes from %i.', num, cluster_ids[0])
