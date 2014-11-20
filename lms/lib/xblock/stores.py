import logging

from xblock.exceptions import KeyValueMultiSaveError, InvalidScopeError
from xblock.fields import Scope
from xblock.runtime import KeyValueStore

log = logging.getLogger(__name__)


class CassandraUserStateKeyValueStore(KeyValueStore):
    """
    This KeyValueStore will read and write data in the following scopes to cassandra
        Scope.user_state

    Access to any other scopes will raise an InvalidScopeError
    """

    def __init__(self, session, table_name):
        """
        """
        self._session = session
        self._table_name = table_name

    _allowed_scopes = (
        Scope.user_state,
    )

    @classmethod
    def _check_scope(cls, key):
        if key.scope not in cls._allowed_scopes:
            raise InvalidScopeError(key)

    @staticmethod
    def _selectors_from_key(key):
        """
        parses a kvs key to retrieve the values we need as a dict:
            student_id
            course_key
            block_type
            usage_key
            field_name
        """
        return {
            'student_id': key.user_id,
            'course_key': unicode(key.block_scope_id.course_key),
            'block_type': key.block_scope_id.block_type,
            'usage_key': unicode(key.block_scope_id),
            'field_name': key.field_name,
        }

    def get(self, key):
        """
        """
        self._check_scope(key)

        selectors = self._selectors_from_key(key)
        where = ' AND '.join(('{}=%({})s'.format(k, k) for k in selectors))
        query = "SELECT field_value FROM {} WHERE {}".format(
            self._table_name,
            where,
        )
        log.info(query)
        rows = list(self._session.execute(query, selectors))
        return rows[0].field_value if len(rows) else None

    def set(self, key, value):
        """
        Set a single value in the KeyValueStore
        """
        self._check_scope(key)

        values = self._selectors_from_key(key)
        values.update({'field_value': value})
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            self._table_name,
            ', '.join(values.keys()),
            ', '.join(('%({})s'.format(k) for k in values))
        )
        log.info(query)
        self._session.execute(query, values)

    def set_many(self, kv_dict):
        """
        Provide a bulk save mechanism.

        `kv_dict`: A dictionary of dirty fields that maps
          xblock.KvsFieldData._key : value

        """
        saved_fields = []
        for key, field_value in kv_dict.iteritems():
            # Check field for validity
            try:
                # Save the field object that we made above
                self.set(key, field_value)
                # If save is successful on this scope, add the saved fields to
                # the list of successful saves
                saved_fields.append(key.field_name)
            except:
                log.exception('Error saving fields %r', key)
                raise KeyValueMultiSaveError(saved_fields)

    def delete(self, key):
        """
        """
        self._check_scope(key)

        selectors = self._selectors_from_key(key)
        where = ' AND '.join(('{}=%({})s'.format(k, k) for k in selectors))
        self._session.execute(
            "DELETE FROM {} WHERE {}".format(
                self._table_name,
                where,
            ),
            selectors,
        )

    def has(self, key):
        """
        """
        return self.get(key) is not None
