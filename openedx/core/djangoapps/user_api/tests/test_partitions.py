"""
Test the partitions and partitions service

"""

from collections import defaultdict
from unittest import TestCase

from openedx.core.djangoapps.user_api.partitions import RandomUserPartitionScheme, UserPartitionError
from student.tests.factories import UserFactory
from xmodule.partitions.partitions import Group, UserPartition


class MemoryUserService(object):
    """
    An implementation of a user service that uses an in-memory dictionary for storage
    """
    COURSE_SCOPE = 'course'

    def __init__(self):
        self._tags = defaultdict(dict)

    def get_course_tag(self, __, course_id, key):
        """Sets the value of ``key`` to ``value``"""
        return self._tags[course_id].get(key)

    def set_course_tag(self, __, course_id, key, value):
        """Gets the value of ``key``"""
        self._tags[course_id][key] = value


class TestRandomUserPartitionScheme(TestCase):
    """
    Test getting a user's group out of a partition
    """

    MOCK_COURSE_ID = "mock-course-id"

    def setUp(self):
        groups = [Group(0, 'Group 1'), Group(1, 'Group 2')]
        self.partition_id = 0

        RandomUserPartitionScheme.user_tags_service = MemoryUserService()
        self.user_partition = UserPartition(
            self.partition_id,
            'Test Partition',
            'for testing purposes',
            groups,
            scheme=RandomUserPartitionScheme
        )

        self.user = UserFactory.create()

    def test_get_group_for_user(self):
        # get a group assigned to the user
        group1_id = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, self.user_partition)

        # make sure we get the same group back out every time
        for __ in range(0, 10):
            group2_id = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, self.user_partition)
            self.assertEqual(group1_id, group2_id)

    def test_empty_partition(self):
        empty_partition = UserPartition(
            self.partition_id,
            'Test Partition',
            'for testing purposes',
            [],
            scheme=RandomUserPartitionScheme
        )
        # get a group assigned to the user
        with self.assertRaisesRegexp(UserPartitionError, "Cannot assign user to an empty user partition"):
            RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, empty_partition)

    def test_user_in_deleted_group(self):
        # get a group assigned to the user - should be group 0 or 1
        old_group = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, self.user_partition)
        self.assertIn(old_group.id, [0, 1])

        # Change the group definitions! No more group 0 or 1
        groups = [Group(3, 'Group 3'), Group(4, 'Group 4')]
        user_partition = UserPartition(self.partition_id, 'Test Partition', 'for testing purposes', groups)

        # Now, get a new group using the same call - should be 3 or 4
        new_group = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, user_partition)
        self.assertIn(new_group.id, [3, 4])

        # We should get the same group over multiple calls
        new_group_2 = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, user_partition)
        self.assertEqual(new_group, new_group_2)

    def test_change_group_name(self):
        # Changing the name of the group shouldn't affect anything
        # get a group assigned to the user - should be group 0 or 1
        old_group = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, self.user_partition)
        self.assertIn(old_group.id, [0, 1])

        # Change the group names
        groups = [Group(0, 'Group 0'), Group(1, 'Group 1')]
        user_partition = UserPartition(
            self.partition_id,
            'Test Partition',
            'for testing purposes',
            groups,
            scheme=RandomUserPartitionScheme
        )

        # Now, get a new group using the same call
        new_group = RandomUserPartitionScheme.get_group_for_user(self.MOCK_COURSE_ID, self.user, user_partition)
        self.assertEqual(old_group.id, new_group.id)
