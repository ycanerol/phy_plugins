"""
Reorder columns in ClusterView and SimilarityView

Specified columns are moved to the right hand side of the cluster view
and similarity view. This also allows to rearrange the order completely
by specifying all column names in `last_columns`, see configuration
below.

The similarity column in the similarity view is added to the table last
(far right), such that there is an additional function below to reset
the table with the desired column order instead.

If present, the column named 'quality' will be squeezed to minimum width
to preserve some space.

Additionally, the text in the columns can be left, right or center
aligned (default here is 'right'). To use up less space the table can
be set to `tight_columns` where the column headers no longer explode the
column widths unnecessarily (False by default).

Configuration:

On first use, a JSON file will be created in the Phy configuration
directory, usually {HOME}/.phy/plugin_reordercolumns.json. The column
names for reordering (`last_columns`), the text alignment
(`text_align`), and the tight column option (`tight_columns`) can be
adjusted there. Here the details:

last_columns : list of str
    List of columns to move to the right hand side

text_align : {'left', 'center', 'right'}
    Align the text within each column

tight_columns : bool
    Whether to squeeze width of all column headers
"""

import json
from phy import IPlugin, connect
from phy.cluster.supervisor import ClusterView
from phy.utils import phy_config_dir
from pathlib import Path
import logging

logger = logging.getLogger('phy')


class ReorderColumns(IPlugin):
    # Load config
    def __init__(self):
        filepath = Path(phy_config_dir()) / 'plugin_reordercolumns.json'

        # Default config
        dflts = {
            'last_columns': ['quality', 'comment'],
            'text_align': 'right',
            'tight_columns': False,
        }

        # Create config file with defaults if it does not exist
        if not filepath.exists():
            logger.debug("Create default config at %s.", filepath)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dflts, f, ensure_ascii=False, indent=4)

        # Load config
        logger.debug("Load %s for config.", filepath)
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                logger.warning("Error decoding JSON: %s", e)
                data = dflts

        self.last_columns = data.get('last_columns', dflts['last_columns'])
        self.text_align = data.get('text_align', dflts['text_align'])
        self.tight_columns = data.get('tight_columns', dflts['tight_columns'])

    def attach_to_controller(self, controller):
        # Reduce width of the quality column/all columns
        qual_idx, cmnt_idx = 999, 999
        if 'quality' in self.last_columns:
            qual_idx = self.last_columns[::-1].index('quality') + 1
        if 'comment' in self.last_columns:
            cmnt_idx = self.last_columns[::-1].index('comment') + 1
        spec = '' if self.tight_columns else f':nth-last-child({qual_idx})'
        ClusterView._styles += """

            table th""" + spec + """, td.quality {
                max-width: 8px;
                overflow: hidden;
            }

            table td {
                text-align: """ + self.text_align + """;
            }

            /* Force comment to be left-aligned */
            table th:nth-last-child(""" + str(cmnt_idx) + """), td.comment {
                text-align: left!important;
            }

        """

        @connect
        def on_controller_ready(sender):
            for col in self.last_columns:
                if col not in controller.supervisor.columns:
                    logger.debug("Add column %s.", col)
                    controller.supervisor.cluster_meta.add_field(col)
                else:
                    controller.supervisor.columns.remove(col)
                controller.supervisor.columns.append(col)

        @connect
        def on_gui_ready(sender, gui):
            """The similarity view requires special rearranging"""

            # Add custom columns after 'similarity'
            columns = controller.supervisor.columns.copy()
            for col in self.last_columns:
                columns.remove(col)
            columns.append('similarity')
            for col in self.last_columns:
                columns.append(col)

            # Recreating the table
            controller.supervisor.similarity_view._reset_table(
                columns=columns, sort=('similarity', 'desc')
            )
