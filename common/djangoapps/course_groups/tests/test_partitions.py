"""
Test the partitions and partitions service

"""

from django.conf import settings
import django.test
from django.test.utils import override_settings
from mock import patch

from student.tests.factories import UserFactory
from xmodule.partitions.partitions import Group, UserPartition
from xmodule.modulestore.django import modulestore, clear_existing_modulestores
from xmodule.modulestore.tests.django_utils import mixed_store_config
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from ..partitions import CohortPartitionScheme
from ..models import CourseUserGroupPartitionGroup
from ..cohorts import add_user_to_cohort
from .helpers import CohortFactory, config_course_cohorts


TEST_DATA_DIR = settings.COMMON_TEST_DATA_ROOT
TEST_MAPPING = {'edX/toy/2012_Fall': 'xml'}
TEST_DATA_MIXED_MODULESTORE = mixed_store_config(TEST_DATA_DIR, TEST_MAPPING)


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class TestCohortPartitionScheme(django.test.TestCase):
    """
    Test the logic for mapping a user to a partition group based on their cohort.
    """

    def setUp(self):
        """
        Regenerate a course with cohort configuration, partition and groups,
        cohorts, and students for each test.
        """
        clear_existing_modulestores()
        self.course_key = SlashSeparatedCourseKey("edX", "toy", "2012_Fall")
        config_course_cohorts(modulestore().get_course(self.course_key), [], cohorted=True)

        self.groups = [Group(10, 'Group 10'), Group(20, 'Group 20')]
        self.user_partition = UserPartition(
            0,
            'Test Partition',
            'for testing purposes',
            self.groups,
            scheme=CohortPartitionScheme
        )
        self.students = [UserFactory.create() for _ in range(3)]
        self.cohorts = [CohortFactory(course_id=self.course_key) for _ in range(2)]

    def _assignCohortToPartitionGroup(self, cohort, partition, group):
        """
        utility for creating cohort -> partition group mappings
        """
        CourseUserGroupPartitionGroup(
            course_user_group=cohort,
            partition_id=partition.id,
            group_id=group.id,
        ).save()

    def _unassignCohortPartitionGroup(self, cohort):
        """
        utility for removing cohort -> partition group mappings
        """
        CourseUserGroupPartitionGroup.objects.filter(course_user_group=cohort).delete()

    def test_student_cohort_assignment(self):
        """
        Test that the CohortPartitionScheme returns the correct group for a
        student when the student is moved in and out of different cohorts.
        """
        self.assertIsNone(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            )
        )
        # place student 0 into cohort 0
        add_user_to_cohort(self.cohorts[0],  self.students[0].username)
        # map cohort 0 to group 0 in the partition
        self._assignCohortToPartitionGroup(
            self.cohorts[0],
            self.user_partition,
            self.groups[0],
        )
        # map cohort 1 to to group 1 in the partition
        self._assignCohortToPartitionGroup(
            self.cohorts[1],
            self.user_partition,
            self.groups[1],
        )
        # check that the mapping places student 0 into partition group 0
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            self.groups[0]
        )
        # move student from cohort 0 to cohort 1
        add_user_to_cohort(self.cohorts[1], self.students[0].username)
        # check that the mapping is correctly updated
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            self.groups[1]
        )
        # move the student out of the cohort
        self.cohorts[1].users.remove(self.students[0])
        # check that the mapping returns nothing again
        self.assertIsNone(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            )
        )

    def test_cohort_partition_group_assignment(self):
        """
        Test that the CohortPartitionScheme returns the correct group for a
        student in a cohort when the cohort mapping is created / moved / deleted.
        """
        # assign user to cohort (but cohort isn't mapped to a partition group yet)
        add_user_to_cohort(self.cohorts[0], self.students[0].username)
        # scheme should not yet find any mapping
        self.assertIsNone(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            )
        )
        # map cohort 0 to group 0
        self._assignCohortToPartitionGroup(
            self.cohorts[0],
            self.user_partition,
            self.groups[0],
        )
        # now the scheme should find a mapping
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            self.groups[0]
        )
        # map cohort 0 to group 1 (first unmap it from group 0)
        self._unassignCohortPartitionGroup(
            self.cohorts[0],
        )
        self._assignCohortToPartitionGroup(
            self.cohorts[0],
            self.user_partition,
            self.groups[1],
        )
        # scheme should pick up the mapping
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            self.groups[1]
        )
        # unmap cohort 0 from anywhere
        self._unassignCohortPartitionGroup(
            self.cohorts[0],
        )
        # scheme should now return nothing
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            None
        )

    def test_partition_changes(self):
        """
        if the name of a user partition is changed, or a group is added to the
        partition, mappings do not break.

        if the name of a group is changed, mappings do not break.

        if the group is deleted (or its id is changed), there's no ref.
        integrity enforced, so any references from cohorts to that group will be
        lost.  A warning should be logged when cohort references are found to
        groups that no longer exist.

        if the user partition is deleted (or its id is changed), there's no ref.
        integrity enforced, so any references from cohorts to that partition's
        groups will be lost.  A warning should be logged when cohort references
        are found to partitions that no longer exist.
        """
        # map cohort 0 to group 0
        self._assignCohortToPartitionGroup(
            self.cohorts[0],
            self.user_partition,
            self.groups[0],
        )
        # place student 0 into cohort 0
        add_user_to_cohort(self.cohorts[0], self.students[0].username)
        # check mapping is correct
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                self.user_partition,
            ),
            self.groups[0]
        )

        # to simulate a non-destructive configuration change on the course, create
        # a new partition with the same id and scheme but with groups renamed and
        # a group added
        new_groups = [Group(10, 'New Group 10'), Group(20, 'New Group 20'), Group(30, 'New Group 30')]
        new_user_partition = UserPartition(
            0,  # same id
            'Different Partition',
            'dummy',
            new_groups,
            scheme=CohortPartitionScheme,
        )
        # the mapping should still be correct
        self.assertEqual(
            CohortPartitionScheme.get_group_for_user(
                self.course_key,
                self.students[0],
                new_user_partition,
            ),
            new_groups[0]
        )

        # to simulate a destructive change on the course, create a new partition
        # with the same id, but different groups (disjoint ids).
        new_groups = [Group(11, 'Not Group 10'), Group(21, 'Not Group 20')]
        new_user_partition = UserPartition(
            0,  # same id
            'Another Partition',
            'dummy',
            new_groups,
            scheme=CohortPartitionScheme,
        )
        # the partition will be found since it has the same id, but the group
        # ids aren't present anymore, so the scheme returns None (and logs a
        # warning)
        with patch('course_groups.partitions.log') as mock_log:
            self.assertIsNone(
                CohortPartitionScheme.get_group_for_user(
                    self.course_key,
                    self.students[0],
                    new_user_partition,
                ),
                None
            )
            self.assertTrue(mock_log.warn.called)
            self.assertRegexpMatches(mock_log.warn.call_args[0][0], 'group not found')

        # to simulate another destructive change on the course, create a new
        # partition with a different id, but using the same groups.
        new_groups = [Group(10, 'Group 10'), Group(20, 'Group 20')] # same ids
        new_user_partition = UserPartition(
            1,  # different id
            'Moved Partition',
            'dummy',
            new_groups,
            scheme=CohortPartitionScheme,
        )
        # the partition will not be found even though the group ids match, so the
        # scheme returns None (and logs a warning).
        with patch('course_groups.partitions.log') as mock_log:
            self.assertIsNone(
                CohortPartitionScheme.get_group_for_user(
                    self.course_key,
                    self.students[0],
                    new_user_partition,
                ),
                None
            )
            self.assertTrue(mock_log.warn.called)
            self.assertRegexpMatches(mock_log.warn.call_args[0][0], 'partition mismatch')
