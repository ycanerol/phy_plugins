from phy import IPlugin, connect

import logging
import os
import numpy as np

import platform

from pathlib import Path
from subprocess import Popen

from scipy.cluster.vq import kmeans2, whiten

logger = logging.getLogger('phy')

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    logger.warn("Package pandas not installed.")
try:
    from phy.utils.config import phy_config_dir
except ImportError:  # pragma: no cover
    logger.warn("phy_config_dir not available.")

class Recluster(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        #@controller.supervisor.connect
        #def on_create_cluster_views():
        def on_gui_ready(sender,gui):

            @controller.supervisor.actions.add(shortcut='alt+q', prompt=True, prompt_default=lambda: 2)
            def K_means_clustering(kmeanclusters):
                """Select number of clusters.

                Example: `2`

                """
                logger.warn("Running K-means clustering")

                cluster_ids = controller.supervisor.selected

                spike_ids = controller.selector.select_spikes(cluster_ids)
                s = controller.supervisor.clustering.spikes_in_clusters(cluster_ids)
                data = controller.model._load_features()
                data3 = data.data[spike_ids]
                data2 = np.reshape(data3,(data3.shape[0],data3.shape[1]*data3.shape[2]))
                whitened = whiten(data2)
                clusters_out,label = kmeans2(whitened,kmeanclusters)
                assert s.shape == label.shape

                controller.supervisor.actions.split(s,label)
                logger.warn("K means clustering complete")

            @controller.supervisor.actions.add(shortcut='alt+a', prompt=True, prompt_default=lambda: 2)
            def K_means_clustering_amplitude(n_clusters):
                """Split based on template amplitudes.
                Select number of clusters.

                Example: `2`"""

                # Selected clusters across the cluster view and similarity view.
                cluster_ids = controller.supervisor.selected

                # Get the amplitudes, using the same controller method as what the amplitude view
                # is using.
                # Note that we need load_all=True to load all spikes from the selected clusters,
                # instead of just the selection of them chosen for display.
                bunchs = controller._amplitude_getter(cluster_ids, name='template', load_all=True)

                # We get the spike ids and the corresponding spike template amplitudes.
                # NOTE: in this example, we only consider the first selected cluster.
                spike_ids = bunchs[0].spike_ids
                y = bunchs[0].amplitudes
                y_whitened = whiten(y.reshape((-1, 1)))

                # We perform the clustering algorithm, which returns an integer for each
                # subcluster.
                clusters_out, labels = kmeans2(y_whitened, n_clusters)

                assert spike_ids.shape == labels.shape

                # We split according to the labels.
                controller.supervisor.actions.split(spike_ids, labels)


            #@controller.supervisor.actions.add(shortcut='alt+x')
            @controller.supervisor.actions.add(shortcut='alt+x', prompt=True, prompt_default=lambda: 14)
            def MahalanobisDist(thres_in):
                """Select threshold in STDs.

                Example: `14`

                """
                logger.warn("Removing outliers by Mahalanobis distance")

                def MahalanobisDistCalc2(x, y):
                    covariance_xy = np.cov(x,y, rowvar=0)
                    inv_covariance_xy = np.linalg.inv(covariance_xy)
                    xy_mean = np.mean(x),np.mean(y)
                    x_diff = np.array([x_i - xy_mean[0] for x_i in x])
                    y_diff = np.array([y_i - xy_mean[1] for y_i in y])
                    diff_xy = np.transpose([x_diff, y_diff])
                    md = []
                    for i in range(len(diff_xy)):
                        md.append(np.sqrt(np.dot(np.dot(np.transpose(diff_xy[i]),inv_covariance_xy),diff_xy[i])))
                    return md

                def MahalanobisDistCalc(X, Y):
                    rx = X.shape[0]
                    cx = X.shape[1]
                    ry = Y.shape[0]
                    cy = Y.shape[1]

                    m = np.mean(X, axis=0)
                    M = np.tile(m,(ry,1))
                    C = X - np.tile(m,(rx,1))
                    Q, R = np.linalg.qr(C)
                    ri,ri2,ri3,ri4 = np.linalg.lstsq(np.transpose(R),np.transpose(Y-M))
                    d = np.transpose(np.sum(ri*ri, axis=0)).dot(rx-1)
                    return d

                cluster_ids = controller.supervisor.selected
                spike_ids = controller.selector.select_spikes(cluster_ids)
                s = controller.supervisor.clustering.spikes_in_clusters(cluster_ids)
                data = controller.model._load_features()
                data3 = data.data[spike_ids]
                data2 = np.reshape(data3,(data3.shape[0],data3.shape[1]*data3.shape[2]))
                if data2.shape[0] < data2.shape[1]:
                    logger.warn("Error: Not enought spikes in the cluster!")
                    return

                MD = MahalanobisDistCalc(data2,data2)
                #threshold = 16**2
                threshold = thres_in**2
                outliers  = np.where(MD > threshold)[0]
                outliers2 = np.ones(len(s),dtype=int)
                outliers2[outliers] = 2
                logger.info("Outliers detected: %d.", len(outliers))
                controller.supervisor.actions.split(s,outliers2)
