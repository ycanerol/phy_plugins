"""
Draw lines for beginning of each stimuli
"""
import os

from phy import IPlugin, connect
from phy.cluster.views.amplitude import AmplitudeView as AmplitudeView
from phy.plot.visuals import LineVisual
import logging

import numpy as np

import h5py

logger = logging.getLogger('phy')

class StimulusBounds(IPlugin):

    def attach_to_controller(self, controller):

        @connect
        def on_gui_ready(sender, gui):

            amp_view = gui.get_view(AmplitudeView)
            line_color = (.15, .15, .15, 1)

            def read_stimulus_bounds():
                """
                Read the stimulus boundaries from the bininfo.mat file

                """

                folder = controller.dir_path

                with h5py.File(os.path.join(folder, 'bininfo.mat'), mode='r') as f:
                    stim_samples = f['bininfo']['stimsamples'][()].astype(int)

                sample_rate = int(controller.model.sample_rate)

                stim_bounds = stim_samples / sample_rate

                return stim_bounds


            def draw_lines():
                stim_bounds = read_stimulus_bounds()
                nlines = stim_bounds.shape[0]
                data_bounds = amp_view.data_bounds
                pos = np.zeros((stim_bounds))

                lines = LineVisual(pos,
                                    color=line_color,
                                    data_bounds=data_bounds)
                amp_view.canvas.add_visual(lines)
