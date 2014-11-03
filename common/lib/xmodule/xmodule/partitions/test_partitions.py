"""
Test the partitions and partitions service

"""

from collections import defaultdict
from unittest import TestCase
from mock import Mock

from xmodule.partitions.partitions import (
    Group, UserPartition, UserPartitionScheme
)
from xmodule.partitions.partitions_service import PartitionService


class TestGroup(TestCase):
    """Test constructing groups"""
    def test_construct(self):
        test_id = 10
        name = "Grendel"
        group = Group(test_id, name)
        self.assertEqual(group.id, test_id)
        self.assertEqual(group.name, name)

    def test_string_id(self):
        test_id = "10"
        name = "Grendel"
        group = Group(test_id, name)
        self.assertEqual(group.id, 10)

    def test_to_json(self):
        test_id = 10
        name = "Grendel"
        group = Group(test_id, name)
        jsonified = group.to_json()
        act_jsonified = {
            "id": test_id,
            "name": name,
            "version": group.VERSION
        }
        self.assertEqual(jsonified, act_jsonified)

    def test_from_json(self):
        test_id = 5
        name = "Grendel"
        jsonified = {
            "id": test_id,
            "name": name,
            "version": Group.VERSION
        }
        group = Group.from_json(jsonified)
        self.assertEqual(group.id, test_id)
        self.assertEqual(group.name, name)

    def test_from_json_broken(self):
        test_id = 5
        name = "Grendel"
        # Bad version
        jsonified = {
            "id": test_id,
            "name": name,
            "version": 9001
        }
        with self.assertRaisesRegexp(TypeError, "has unexpected version"):
            Group.from_json(jsonified)

        # Missing key "id"
        jsonified = {
            "name": name,
            "version": Group.VERSION
        }
        with self.assertRaisesRegexp(TypeError, "missing value key 'id'"):
            Group.from_json(jsonified)

        # Has extra key - should not be a problem
        jsonified = {
            "id": test_id,
            "name": name,
            "version": Group.VERSION,
            "programmer": "Cale"
        }
        group = Group.from_json(jsonified)
        self.assertNotIn("programmer", group.to_json())


class MockUserPartitionScheme(UserPartitionScheme):
    """
    Mock user partition scheme
    """

    def __init__(self, current_group=None, **kwargs):
        super(MockUserPartitionScheme, self).__init__(**kwargs)
        self.current_group = current_group

    name = "mock"
    IS_DYNAMIC = True

    def get_group_for_user(self, user_partition):    # pylint: disable=unused-argument
        """
        Returns the group to which the current user should be assigned.
        """
        return self.current_group


class TestUserPartition(TestCase):
    """Test constructing UserPartitions"""

    MOCK_ID = 1
    MOCK_NAME = "Mock Partition"
    MOCK_DESCRIPTION = "for testing purposes"
    MOCK_GROUPS = [Group(0, 'Group 1'), Group(1, 'Group 2')]
    MOCK_SCHEME = "mock"

    def test_construct(self):
        user_partition = UserPartition(
            self.MOCK_ID, self.MOCK_NAME, self.MOCK_DESCRIPTION, self.MOCK_GROUPS
        )
        self.assertEqual(user_partition.id, self.MOCK_ID)    # pylint: disable=no-member
        self.assertEqual(user_partition.name, self.MOCK_NAME)
        self.assertEqual(user_partition.description, self.MOCK_DESCRIPTION)    # pylint: disable=no-member
        self.assertEqual(user_partition.groups, self.MOCK_GROUPS)    # pylint: disable=no-member

    def test_string_id(self):
        user_partition = UserPartition(
            "70", self.MOCK_NAME, self.MOCK_DESCRIPTION, self.MOCK_GROUPS
        )
        self.assertEqual(user_partition.id, 70)    # pylint: disable=no-member

    def test_to_json(self):
        user_partition = UserPartition(
            self.MOCK_ID, self.MOCK_NAME, self.MOCK_DESCRIPTION, self.MOCK_GROUPS,
            scheme=MockUserPartitionScheme()
        )

        jsonified = user_partition.to_json()
        act_jsonified = {
            "id": self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": user_partition.VERSION,
            "scheme": self.MOCK_SCHEME
        }
        self.assertEqual(jsonified, act_jsonified)

    def test_from_json(self):
        jsonified = {
            "id": self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": UserPartition.VERSION,
            "scheme": "random",
        }
        user_partition = UserPartition.from_json(jsonified)
        self.assertEqual(user_partition.id, self.MOCK_ID)    # pylint: disable=no-member
        self.assertEqual(user_partition.name, self.MOCK_NAME)    # pylint: disable=no-member
        self.assertEqual(user_partition.description, self.MOCK_DESCRIPTION)    # pylint: disable=no-member
        for act_group in user_partition.groups:    # pylint: disable=no-member
            self.assertIn(act_group.id, [0, 1])
            exp_group = self.MOCK_GROUPS[act_group.id]
            self.assertEqual(exp_group.id, act_group.id)
            self.assertEqual(exp_group.name, act_group.name)

    def test_version_upgrade(self):
        # Version 1 partitions did not have a scheme specified
        jsonified = {
            "id": self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": 1,
        }
        user_partition = UserPartition.from_json(jsonified)
        self.assertEqual(user_partition.scheme.name, "random")    # pylint: disable=no-member

    def test_from_json_broken(self):
        # Missing field
        jsonified = {
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": UserPartition.VERSION,
            "scheme": self.MOCK_SCHEME,
        }
        with self.assertRaisesRegexp(TypeError, "missing value key 'id'"):
            UserPartition.from_json(jsonified)

        # Missing scheme
        jsonified = {
            'id': self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": UserPartition.VERSION,
        }
        with self.assertRaisesRegexp(TypeError, "missing value key 'scheme'"):
            UserPartition.from_json(jsonified)

        # Invalid scheme
        jsonified = {
            'id': self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": UserPartition.VERSION,
            "scheme": "no_such_scheme",
        }
        with self.assertRaisesRegexp(TypeError, "Unrecognized scheme"):
            UserPartition.from_json(jsonified)

        # Wrong version (it's over 9000!)
        # Wrong version (it's over 9000!)
        jsonified = {
            'id': self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": 9001,
            "scheme": self.MOCK_SCHEME,
        }
        with self.assertRaisesRegexp(TypeError, "has unexpected version"):
            user_partition = UserPartition.from_json(jsonified)

        # Has extra key - should not be a problem
        jsonified = {
            'id': self.MOCK_ID,
            "name": self.MOCK_NAME,
            "description": self.MOCK_DESCRIPTION,
            "groups": [group.to_json() for group in self.MOCK_GROUPS],
            "version": UserPartition.VERSION,
            "scheme": "random",
            "programmer": "Cale",
        }
        user_partition = UserPartition.from_json(jsonified)
        self.assertNotIn("programmer", user_partition.to_json())


class StaticPartitionService(PartitionService):
    """
    Mock PartitionService for testing.
    """
    def __init__(self, partitions, **kwargs):
        super(StaticPartitionService, self).__init__(**kwargs)
        self._partitions = partitions

    @property
    def course_partitions(self):
        return self._partitions


class MemoryUserTagsService(object):
    """
    An implementation of a user_tags XBlock service that
    uses an in-memory dictionary for storage
    """
    COURSE_SCOPE = 'course'

    def __init__(self):
        self._tags = defaultdict(dict)

    def get_tag(self, scope, key):
        """Sets the value of ``key`` to ``value``"""
        print 'GETTING', scope, key, self._tags
        return self._tags[scope].get(key)

    def set_tag(self, scope, key, value):
        """Gets the value of ``key``"""
        self._tags[scope][key] = value
        print 'SET', scope, key, value, self._tags


class TestPartitionsService(TestCase):
    """
    Test getting a user's group out of a partition
    """

    def setUp(self):
        groups = [Group(0, 'Group 1'), Group(1, 'Group 2')]
        self.partition_id = 0

        self.user_tags_service = MemoryUserTagsService()
        user_partition = UserPartition(self.partition_id, 'Test Partition', 'for testing purposes', groups)

        self.mock_partition_id = 1
        self.mock_partition = UserPartition(
            self.mock_partition_id,
            'Mock Partition',
            'Mock partition for testing',
            [Group(0, 'Group 1'), Group(1, 'Group 2')],
            MockUserPartitionScheme()
        )

        self.partitions_service = StaticPartitionService(
            [user_partition, self.mock_partition],
            user_tags_service=self.user_tags_service,
            course_id=Mock(),
            track_function=Mock()
        )

    def test_get_user_group_id_for_partition(self):
        # get a group assigned to the user
        group1_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)

        # make sure we get the same group back out every time
        for __ in range(0, 10):
            group2_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
            self.assertEqual(group1_id, group2_id)

        # test that we error if given an invalid partition id
        with self.assertRaises(ValueError):
            self.partitions_service.get_user_group_id_for_partition(3)

    def test_get_dynamic_user_group_id_for_partition(self):
        # assign the first group to be returned
        groups = self.mock_partition.groups    # pylint: disable=no-member
        self.mock_partition.scheme.current_group = groups[0]    # pylint: disable=no-member

        # get a group assigned to the user
        group1_id = self.partitions_service.get_user_group_id_for_partition(self.mock_partition_id)
        self.assertEqual(group1_id, groups[0].id)

        # switch to the second group and verify that it is returned for the user
        self.mock_partition.scheme.current_group = groups[1]    # pylint: disable=no-member
        group2_id = self.partitions_service.get_user_group_id_for_partition(self.mock_partition_id)
        self.assertEqual(group2_id, groups[1].id)

    def test_user_in_deleted_group(self):
        # get a group assigned to the user - should be group 0 or 1
        old_group_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
        self.assertIn(old_group_id, [0, 1])

        # Change the group definitions! No more group 0 or 1
        groups = [Group(3, 'Group 3'), Group(4, 'Group 4')]
        user_partition = UserPartition(self.partition_id, 'Test Partition', 'for testing purposes', groups)
        self.partitions_service = StaticPartitionService(
            [user_partition],
            user_tags_service=self.user_tags_service,
            course_id=Mock(),
            track_function=Mock()
        )

        # Now, get a new group using the same call - should be 3 or 4
        new_group_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
        self.assertIn(new_group_id, [3, 4])

        # We should get the same group over multiple calls
        new_group_2 = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
        self.assertEqual(new_group_id, new_group_2)

    def test_change_group_name(self):
        # Changing the name of the group shouldn't affect anything
        # get a group assigned to the user - should be group 0 or 1
        old_group_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
        self.assertIn(old_group_id, [0, 1])

        # Change the group names
        groups = [Group(0, 'Group 0'), Group(1, 'Group 1')]
        user_partition = UserPartition(self.partition_id, 'Test Partition', 'for testing purposes', groups)
        self.partitions_service = StaticPartitionService(
            [user_partition],
            user_tags_service=self.user_tags_service,
            course_id=Mock(),
            track_function=Mock()
        )

        # Now, get a new group using the same call
        new_group_id = self.partitions_service.get_user_group_id_for_partition(self.partition_id)
        self.assertEqual(old_group_id, new_group_id)
