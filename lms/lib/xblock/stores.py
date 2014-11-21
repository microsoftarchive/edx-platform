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

    def __init__(self, driver):
        """
        """
        self._driver = driver

    _allowed_scopes = (
        Scope.user_state,
    )

    @classmethod
    def _check_scope(cls, key):
        if key.scope not in cls._allowed_scopes:
            raise InvalidScopeError(key)

    @staticmethod
    def _criteria_from_key(key):
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
        criteria = self._criteria_from_key(key)
        return self._driver.get_current_field_value(**criteria)

    def set(self, key, value):
        """
        Set a single value in the KeyValueStore
        """
        self._check_scope(key)
        criteria = self._criteria_from_key(key)
        return self._driver.set_current_field_value(field_value=value, **criteria)

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
        criteria = self._criteria_from_key(key)
        return self._driver.delete_current_field_value(**criteria)

    def has(self, key):
        """
        """
        return self.get(key) is not None
