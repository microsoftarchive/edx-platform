"""
Provides partition support to the user service.
"""

import random
from xmodule.partitions.partitions import UserPartitionScheme


class RandomUserPartitionScheme(UserPartitionScheme):
    """
    This scheme randomly assigns users into the partition's groups.
    """
    SCHEME_ID = 'random'

    def __init__(self, extension=None):
        super(RandomUserPartitionScheme, self).__init__(extension=extension)
        self.random = random.Random()

    def get_group_for_user(self, user_partition):
        """
        Returns the group to which the current user should be assigned.
        """
        # pylint: disable=fixme
        # TODO: had a discussion in arch council about making randomization more
        # deterministic (e.g. some hash).  Could do that, but need to be careful not
        # to introduce correlation between users or bias in generation.
        return self.random.choice(user_partition.groups)
