"""
Show all non-noisy channels in waveform view

Modified from ExampleNspikesViewsPlugin
"""

from phy import IPlugin


class WaveformThr(IPlugin):
    def attach_to_controller(self, controller):
        controller.model.n_closest_channels = 256

        # Select the channels whose mean amplitude is greater than this
        # fraction of the peak amplitude on the best channel
        controller.model.amplitude_threshold = 0.04
