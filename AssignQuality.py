"""Show how to write a custom split action."""

from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class AssignQuality(IPlugin):
    def assignQuality(self, controller, quality=0):
        # Assign the label to all selected clusters
        controller.supervisor.label('quality',
                                    str(quality) if quality else '')
        if quality:
            controller.supervisor.label('group', 'good')
            logger.info('Assign quality of %i', quality)
        else:
            controller.supervisor.label('group', 'noise')
            logger.info('Removed quality assignment')

    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            """Quick assign selected clusters to a quality or to noise"""

            @controller.supervisor.actions.add(shortcut='alt+1')
            def Assign_quality_1():
                self.assignQuality(controller, 1)

            @controller.supervisor.actions.add(shortcut='alt+2')
            def Assign_quality_2():
                self.assignQuality(controller, 2)

            @controller.supervisor.actions.add(shortcut='alt+3')
            def Assign_quality_3():
                self.assignQuality(controller, 3)

            @controller.supervisor.actions.add(shortcut='alt+4')
            def Assign_quality_4():
                self.assignQuality(controller, 4)

            @controller.supervisor.actions.add(shortcut='alt+5')
            def Put_to_noise():
                self.assignQuality(controller, 0)
