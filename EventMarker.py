"""
Add event markers to the amplitude view

The event markers are read from the file `eventmarkers.txt`. The file is
expected to contain one event in seconds per line. Optionally,
corresponding names can be supplied in `eventmarkernames.txt`.

The event markers may be toggled on/off from the amplitude view menu or
by keyboard shortcut.
"""

from phy import IPlugin, connect
from phy.cluster.views import AmplitudeView, TraceView
from phy.plot.visuals import LineVisual, TextVisual
from phy.plot.transform import _fix_coordinate_in_visual
import logging
import numpy as np

logger = logging.getLogger('phy')


class EventMarker(IPlugin):
    # Line color of the event markers
    line_color = (1, 1, 1, 0.75)

    def attach_to_controller(self, controller):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, AmplitudeView):
                # Create batch of vertical lines (full height)
                self.line_visual = LineVisual()
                _fix_coordinate_in_visual(self.line_visual, 'y')
                view.canvas.add_visual(self.line_visual)

                # Create batch of annotative text
                self.text_visual = TextVisual(self.line_color)
                _fix_coordinate_in_visual(self.text_visual, 'y')
                self.text_visual.inserter.insert_vert(
                    'gl_Position.x += 0.005;', 'after_transforms')
                view.canvas.add_visual(self.text_visual)

                @view.actions.add(shortcut='alt+b', checkable=True,
                                  name='Toggle event markers')
                def toggle(on):
                    """Toggle event markers"""
                    # Use `show` and `hide` instead of `toggle` here in
                    # case synchronization issues
                    if on:
                        logger.debug('Toggle on markers.')
                        self.line_visual.show()
                        self.text_visual.show()
                    else:
                        logger.debug('Toggle off markers.')
                        self.line_visual.hide()
                        self.text_visual.hide()
                    view = gui.get_view(AmplitudeView)
                    view.canvas.update()

                @view.actions.add(shortcut='shift+alt+e', prompt=True,
                                  name='Go to event', alias='ge')
                def go_to_event(eventnr):
                    trace_view_go = gui.get_view(TraceView).go_to
                    if eventnr >0 and eventnr <= events.shape[0]:
                        trace_view_go(events[eventnr-1])


                # Disable the menu until events are successfully added
                view.actions.disable('Toggle event markers')

                # Read event markers from file
                filename = controller.dir_path / 'eventmarkers.txt'
                try:
                    events = np.loadtxt(filename, usecols=0)
                except (FileNotFoundError, OSError):
                    logger.warn('Event marker file not found: `%s`.',
                                filename)
                    return

                # Create list of event names
                labels = list(map(str, range(1, events.size + 1)))

                # Read event names from file (if present)
                filename = controller.dir_path / 'eventmarkernames.txt'
                try:
                    eventnames = np.loadtxt(filename, usecols=0, dtype=str,
                                            max_rows=events.size)
                    labels[:eventnames.size] = eventnames
                except (FileNotFoundError, OSError):
                    logger.info('Event marker names file not found (optional):'
                                ' `%s`. Fall back to numbering.', filename)

                # # Obtain event times from samples
                # events /= int(controller.model.sample_rate)

                logger.debug('Add event markers to amplitude view.')

                # Obtain horizontal positions
                x = -1 + 2 * events / view.duration
                x = x.repeat(4, 0).reshape(-1, 4)
                x[:, 1::2] = 1, -1

                # Add lines and update view
                self.line_visual.reset_batch()
                self.line_visual.add_batch_data(pos=x, color=self.line_color)
                view.canvas.update_visual(self.line_visual)

                # Add text and update view
                self.text_visual.reset_batch()
                self.text_visual.add_batch_data(pos=x[:, :2], anchor=(1, -1),
                                                text=labels)
                view.canvas.update_visual(self.text_visual)

                # Finally enable the menu
                logger.debug('Enable menu item.')
                view.actions.enable('Toggle event markers')
                view.actions.get('Toggle event markers').toggle()
