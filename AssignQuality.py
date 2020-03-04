"""
Quick assign quality to selected clusters

There are 4 quality levels (1 to 4). The assignment triggers two
actions: the column 'quality' is set to the requested level and the
clusters are assigned to the group 'good'. This means that reverting the
assignment requires two 'undo' steps in action history.

Removing the assignment both removes the quality label and the group
assignment (two actions).
"""

from phy import IPlugin, connect
import logging

logger = logging.getLogger('phy')


class AssignQuality(IPlugin):
    def assignQuality(self, controller, quality=None):
        """Assign the label to all selected clusters"""
        selection = controller.supervisor.selected

        # Safety check in case there was no prior selection
        if not selection:
            return

        # Assign quality
        controller.supervisor.label('quality',
                                    str(quality) if quality else None)

        # Obtain sub selection of good clusters
        if not isinstance(selection, list):
            selection = list(selection)
        sel_good = [ci for ci, ll
                    in controller.supervisor.get_labels('group').items()
                    if ci in selection and ll == 'good']

        # (Un-)assign group membership
        if quality:
            if len(sel_good) != len(selection):
                controller.supervisor.label('group', 'good')
            logger.info('Assign quality of %i to clusters %s.', quality,
                        ', '.join(map(str, selection)))
        else:
            controller.supervisor.label('group', None, sel_good)
            logger.info('Remove quality assignment from clusters %s.',
                        ', '.join(map(str, selection)))

    def attach_to_controller(self, controller):
        @connect
        def on_gui_ready(sender, gui):
            @controller.supervisor.actions.add(shortcut='alt+1',
                                               submenu='Assign quality')
            def Assign_quality_1():
                self.assignQuality(controller, 1)

            @controller.supervisor.actions.add(shortcut='alt+2',
                                               submenu='Assign quality')
            def Assign_quality_2():
                self.assignQuality(controller, 2)

            @controller.supervisor.actions.add(shortcut='alt+3',
                                               submenu='Assign quality')
            def Assign_quality_3():
                self.assignQuality(controller, 3)

            @controller.supervisor.actions.add(shortcut='alt+4',
                                               submenu='Assign quality')
            def Assign_quality_4():
                self.assignQuality(controller, 4)

            @controller.supervisor.actions.add(shortcut='alt+5',
                                               submenu='Assign quality')
            def Remove_quality_assigment():
                self.assignQuality(controller, 0)
