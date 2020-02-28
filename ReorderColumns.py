"""Reorder columns in ClusterView and SimilarityView,"""

from phy import IPlugin, connect
from phy.cluster.supervisor import ClusterView


class ReorderColumns(IPlugin):
    def attach_to_controller(self, controller):
        """
        There are a few things to customize:

        last_columns : list of str
            List of columns to move to the right hand side

        tight_columns : bool
            Whether to squeeze width of all column headers

        text_align : {'left', 'center', 'right'}
            Align the text within each column
        """
        last_columns = ['quality', 'comment']
        tight_columns = False
        text_align = 'right'

        # Reduce width of the quality column/all columns
        qual_idx, cmnt_idx = 999, 999
        if 'quality' in last_columns:
            qual_idx = last_columns[::-1].index('quality') + 1
        if 'comment' in last_columns:
            cmnt_idx = last_columns[::-1].index('comment') + 1
        specifier = '' if tight_columns else f':nth-last-child({qual_idx})'
        ClusterView._styles += """

            table th""" + specifier + """, td.quality {
                max-width: 8px;
                overflow: hidden;
            }

            table td {
                text-align: """ + text_align + """;
            }

            /* Force comment to be left-aligned */
            table th:nth-last-child(""" + str(cmnt_idx) + """), td.comment {
                text-align: left!important;
            }

        """

        @connect
        def on_controller_ready(sender):
            for col in last_columns:
                controller.supervisor.columns.remove(col)
                controller.supervisor.columns.append(col)

        @connect
        def on_gui_ready(sender, gui):
            """The similarity view requires special rearranging"""

            # Add custom columns after 'similarity'
            columns = controller.supervisor.columns
            for col in last_columns:
                columns.remove(col)
            columns.append('similarity')
            for col in last_columns:
                columns.append(col)

            # Recreating the table
            controller.supervisor.similarity_view._reset_table(
                columns=columns, sort=('similarity', 'desc')
            )
