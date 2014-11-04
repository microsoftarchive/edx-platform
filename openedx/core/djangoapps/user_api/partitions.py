"""
Provides partition support to the user service.
"""

import random


class RandomUserPartitionScheme(object):
    """
    This scheme randomly assigns users into the partition's groups.
    """
    RANDOM = random.Random()
    IS_DYNAMIC = False

    @classmethod
    def get_group_for_user(self, user_partition):
        """
        Returns the group to which the current user should be assigned.
        """
        # pylint: disable=fixme
        # TODO: had a discussion in arch council about making randomization more
        # deterministic (e.g. some hash).  Could do that, but need to be careful not
        # to introduce correlation between users or bias in generation.
        return RandomUserPartitionScheme.RANDOM.choice(user_partition.groups)
