import unittest

from cassandra.cluster import Cluster, Session
from mock import patch
from opaque_keys.edx.locator import CourseKey, BlockUsageLocator
from xblock.fields import Scope
from xblock.runtime import KeyValueStore

from lms.lib.xblock.stores import CassandraUserStateKeyValueStore

class CassandraUserStateKeyValueStoreTestCase(unittest.TestCase):

    def setUp(self):
        cluster = Cluster()
        self.session = cluster.connect()
        self.session.set_keyspace('mykeyspace')
        self.table_name = 'user_state'
        self.kvs = CassandraUserStateKeyValueStore(self.session, self.table_name)
        self.course_key = CourseKey.from_string('test/course/key')
        self.block_type = 'test_block_type'
        self.block_id = 'test_block_id'
        self._truncate_table()

    def _truncate_table(self):
        self.session.execute("TRUNCATE {}".format(self.table_name))

    def _make_key(
            self,
            user_id,
            field_name,
            scope=None,
            course_key=None,
            block_type=None,
            block_id=None,
    ):
        return KeyValueStore.Key(
            scope or Scope.user_state,
            user_id,
            BlockUsageLocator(
                course_key or self.course_key,
                block_type or self.block_type,
                block_id or self.block_id,
            ),
            field_name
        )

    def test_get(self):
        key = self._make_key(1, 'hello')
        with patch('cassandra.cluster.Session.execute', wraps=self.session.execute) as mock_execute:
            result = self.kvs.get(key)
            self.assertIsNone(result)
            self.assertTrue(mock_execute.called)
            self.assertTrue(mock_execute.call_args[0][0].lower().startswith('select'))

    def test_set(self):
        key = self._make_key(1, 'hello')
        result = self.kvs.get(key)
        self.assertIsNone(result)
        with patch('cassandra.cluster.Session.execute', wraps=self.session.execute) as mock_execute:
            self.kvs.set(key, 'world')
            self.assertTrue(mock_execute.called)
            self.assertTrue(mock_execute.call_args[0][0].lower().startswith('insert'))
        result = self.kvs.get(key)
        self.assertEqual(result, 'world')

    def test_delete(self):
        key = self._make_key(1, 'hello')
        self.kvs.set(key, 'world')
        result = self.kvs.get(key)
        self.assertEqual(result, 'world')
        with patch('cassandra.cluster.Session.execute', wraps=self.session.execute) as mock_execute:
            self.kvs.delete(key)
            self.assertTrue(mock_execute.called)
            self.assertTrue(mock_execute.call_args[0][0].lower().startswith('delete'))
        result = self.kvs.get(key)
        self.assertIsNone(result)

    def test_has(self):
        key = self._make_key(1, 'hello')
        self.assertFalse(self.kvs.has(key))
        self.kvs.set(key, 'world')
        self.assertTrue(self.kvs.has(key))
        self.kvs.delete(key)
        self.assertFalse(self.kvs.has(key))
