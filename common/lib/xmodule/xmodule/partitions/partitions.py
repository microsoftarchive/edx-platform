"""Defines ``Group`` and ``UserPartition`` models for partitioning"""

import random
from collections import namedtuple

# We use ``id`` in this file as the IDs of our Groups and UserPartitions,
# which Pylint disapproves of.
# pylint: disable=invalid-name, redefined-builtin


class Group(namedtuple("Group", "id name")):
    """
    An id and name for a group of students.  The id should be unique
    within the UserPartition this group appears in.
    """
    # in case we want to add to this class, a version will be handy
    # for deserializing old versions.  (This will be serialized in courses)
    VERSION = 1

    def __new__(cls, id, name):
        # pylint: disable=super-on-old-class
        return super(Group, cls).__new__(cls, int(id), name)

    def to_json(self):
        """
        'Serialize' to a json-serializable representation.

        Returns:
            a dictionary with keys for the properties of the group.
        """
        # pylint: disable=no-member
        return {
            "id": self.id,
            "name": self.name,
            "version": Group.VERSION
        }

    @staticmethod
    def from_json(value):
        """
        Deserialize a Group from a json-like representation.

        Args:
            value: a dictionary with keys for the properties of the group.

        Raises TypeError if the value doesn't have the right keys.
        """
        if isinstance(value, Group):
            return value

        for key in ("id", "name", "version"):
            if key not in value:
                raise TypeError("Group dict {0} missing value key '{1}'".format(
                    value, key))

        if value["version"] != Group.VERSION:
            raise TypeError("Group dict {0} has unexpected version".format(
                value))

        return Group(value["id"], value["name"])


class UserPartitionScheme(object):
    """
    The base class for a user partition's scheme. The scheme gets to decide which group
    to put each student into.
    """

    @property
    def is_dynamic(self):
        """
        Returns true if this schema dynamically assigns a user's group. The default is static
        which means that the group is assigned once is then persisted for the user.
        """
        return False

    def __eq__(self, other):
        return type(self) == type(other) and self.scheme_id == other.scheme_id    # pylint: disable=no-member

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.scheme_id)    # pylint: disable=no-member


class RandomUserPartitionScheme(UserPartitionScheme):
    """
    This scheme randomly assigns users into the partition's groups.
    """

    def __init__(self):
        self.random = random.Random()

    @property
    def scheme_id(self):
        """
        Returns the id that identifies this scheme.
        """
        return "random"

    def get_group_for_user(self, user_partition):
        """
        Returns the group to which the current user should be assigned.
        """
        # pylint: disable=fixme
        # TODO: had a discussion in arch council about making randomization more
        # deterministic (e.g. some hash).  Could do that, but need to be careful not
        # to introduce correlation between users or bias in generation.
        return self.random.choice(user_partition.groups)


# The mapping of user partition scheme ids to their implementations.
USER_PARTITION_SCHEMES = {
    "random": RandomUserPartitionScheme(),
}


class UserPartition(namedtuple("UserPartition", "id name description groups scheme")):
    """
    A named way to partition users into groups, primarily intended for running
    experiments.  It is expected that each user will be in at most one group in a
    partition.

    A Partition has an id, name, scheme, description, and a list of groups.
    The id is intended to be unique within the context where these are used. (e.g. for
    partitions of users within a course, the ids should be unique per-course).
    The scheme is used to assign users into groups.
    """
    VERSION = 2
    DEFAULT_SCHEME = USER_PARTITION_SCHEMES["random"]

    def __new__(cls, id, name, description, groups, scheme=DEFAULT_SCHEME):
        # pylint: disable=super-on-old-class
        return super(UserPartition, cls).__new__(cls, int(id), name, description, groups, scheme)

    def to_json(self):
        """
        'Serialize' to a json-serializable representation.

        Returns:
            a dictionary with keys for the properties of the partition.
        """
        # pylint: disable=no-member
        return {
            "id": self.id,
            "name": self.name,
            "scheme": self.scheme.scheme_id,
            "description": self.description,
            "groups": [g.to_json() for g in self.groups],
            "version": UserPartition.VERSION
        }

    @staticmethod
    def from_json(value):
        """
        Deserialize a Group from a json-like representation.

        Args:
            value: a dictionary with keys for the properties of the group.

        Raises TypeError if the value doesn't have the right keys.
        """
        if isinstance(value, UserPartition):
            return value

        for key in ("id", "name", "description", "version", "groups"):
            if key not in value:
                raise TypeError("UserPartition dict {0} missing value key '{1}'".format(value, key))

        if value["version"] == 1:
            # If no scheme was provided, set it to the default ('random')
            scheme = UserPartition.DEFAULT_SCHEME
        elif value["version"] != UserPartition.VERSION:
            raise TypeError("UserPartition dict {0} has unexpected version".format(value))
        else:
            if not "scheme" in value:
                raise TypeError("UserPartition dict {0} missing value key 'scheme'".format(value))
            scheme_id = value["scheme"]
            scheme = USER_PARTITION_SCHEMES.get(scheme_id)
            if not scheme:
                raise TypeError("UserPartition dict {0} has unrecognized scheme {1}".format(value, scheme_id))

        groups = [Group.from_json(g) for g in value["groups"]]

        return UserPartition(
            value["id"],
            value["name"],
            value["description"],
            groups,
            scheme,
        )

    def get_group(self, group_id):
        """
        Returns the group with the specified id.
        """
        for group in self.groups:    # pylint: disable=no-member
            if group.id == group_id:
                return group
        return None
