"""
Add/remove/extend/clear cluster comments

On selection of one cluster the complete comment string is available in
a user input prompt and can be modified and will be replaced. If
selecting multiple clusters, the shared comments will be provided in the
user prompt and only additions are made to the comments of each cluster.

More elaborate actions are possible with prepending the input with '!'
to replace the comments completely with the new input (or clear it if
typing '!' only) and '~' to remove parts of the comments from all
selected clusters.

Multiple comments are separated by a delimiter (see configuration below,
'_' by default). Spaces are not permitted.

Comments are divided into two types: short hand notations (characters),
and custom comments. The short hand notations allow automatic expansion
from single characters to predefined comment parts (see `pairs` below)
for faster work flow. Multiple short hand notations are specified by
grouping the characters together, e.g. asm for a, s and m. The short
hand notations will always be converted back and forth when going back
to editing a comment. To trigger the expansion, they must remain in the
beginning of the string separated from the custom comments (if present)
by the delimiter.

The custom comments can be any words added after the short hand
notations separated by the delimiter (if present). The custom comments
are treated individually if they are separated by the delimiter.

Configuration:

On first use, a JSON file will be created in the Phy configuration
directory, usually {HOME}/.phy/plugin_writecomments.json. The delimiter
and the short hand notation pairs can be adjusted there.
"""

import json
from phy import IPlugin, connect
from phy.utils import phy_config_dir
from pathlib import Path
import logging

logger = logging.getLogger('phy')


class WriteComments(IPlugin):
    # Load config
    def __init__(self):
        filepath = Path(phy_config_dir()) / 'plugin_writecomments.json'

        # Default config
        dflts = dict()
        dflts['delimiter'] = '_'  # Comment delimiter (space is not permitted)
        dflts['pairs'] = {  # Character-comment pairs
            'a': 'axon',
            'm': 'misaligned',
            's': 'spontaneous',
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

        self.delimiter = data.get('delimiter', dflts['delimiter'])
        self.pairs = data.get('pairs', dflts['pairs'])
        self.pairs_inv = {v: k for k, v in self.pairs.items()}

        logger.debug("Available short hand notations are %s.",
                     ', '.join(self.pairs.keys()))

    def load_comments(self, controller):
        """Load selected comments a list of as sets"""
        cluster_ids = controller.supervisor.selected
        allcmt = controller.supervisor.get_labels('comment')

        # Find shared comments (ignoring empty comments)
        comments = []
        for cid in cluster_ids:
            cmt = allcmt[cid].split(self.delimiter) if allcmt[cid] else []
            cmt = set(cmt).difference('')
            comments.append(cmt)
        return comments

    def split_comments(self, comments):
        """Split list of sets into notations and custom comments"""
        pair_set = set(self.pairs.values())
        chars = [c.intersection(pair_set) for c in comments]
        comments = [c.difference(pair_set) for c in comments]
        return chars, comments

    def attach_to_controller(self, controller):
        def get_comments():
            """Fetch common comments among selected clusters"""
            comments = self.load_comments(controller)
            chars, comments = self.split_comments(comments)

            # Keep non-empty comments only
            chars = [p for p in chars if p]
            # comments = [c for c in comments if c]  # Comments not shared

            # Keep shared comments only
            if len(chars) > 0:
                chars = chars[0].intersection(*chars)
            if len(comments) > 0:
                comments = list(comments[0].intersection(*comments))

            # Collapse characters without delimiter
            chars = ''.join(self.pairs_inv[c] for c in chars)
            chars = [chars] if chars else []

            # Join the comments back together
            return self.delimiter.join(chars + comments)

        @connect
        def on_gui_ready(sender, gui):
            @controller.supervisor.actions.add(name='Add comment', alias='com',
                                               shortcut='alt+w', prompt=True,
                                               prompt_default=get_comments)
            def Add_comment(userinput):
                """
                Add comments to selected clusters, prepend with '~' to
                remove comments, prepend with '!' to replace completely,
                type '!' to clear all
                """
                cluster_ids = controller.supervisor.selected

                # Check if replacement if requested
                replace = userinput.startswith('!')
                userinput = userinput.lstrip('!')

                # Check to remove comments
                remove = userinput.startswith('~')
                userinput = userinput.lstrip('~')

                # Clear comments
                if not userinput:
                    controller.supervisor.label('comment', None)
                    logger.info('Clear metadata_comment for clusters %s.',
                                ', '.join(map(str, cluster_ids)))
                    return

                # Otherwise replace/remove/merge with existing
                comments_old = self.load_comments(controller)
                chars_old, comments_old = self.split_comments(comments_old)

                # Extract short hand notations and custom comments
                chars_new, *comments_new = userinput.split(self.delimiter)
                if set(chars_new).issubset(self.pairs.keys()):
                    chars_new = set(self.pairs[c] for c in set(chars_new))
                else:
                    comments_new = [chars_new] + comments_new
                    chars_new = set()
                comments_new = set(comments_new).difference('')

                assert len(cluster_ids) == len(comments_old) == len(chars_old)

                # Merge for each cluster with their previous comments
                comments = []
                for char_old, cmt_old in zip(chars_old, comments_old):
                    if (len(cluster_ids) == 1 or replace) and not remove:
                        # Replace old comment completely
                        char = chars_new
                        comment = comments_new
                    elif remove:
                        # Remove new from old comments
                        char = char_old.difference(chars_new)
                        comment = cmt_old.difference(comments_new)
                    else:
                        # Merge old and new comments
                        char = char_old.union(chars_new)
                        comment = cmt_old.union(comments_new)

                    # Combine final comment string
                    char, comment = list(char), list(comment)
                    comments.append(self.delimiter.join(char + comment))

                if len(set(comments)) == 1:
                    logger.debug('Set the same comment to all clusters')
                    controller.supervisor.label('comment', comments[0])
                else:
                    logger.debug('Set the comments individually')
                    for cid, comment in zip(cluster_ids, comments):
                        controller.supervisor.label('comment', comment,
                                                    cluster_ids=cid)
