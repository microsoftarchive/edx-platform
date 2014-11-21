import json
import logging

log = logging.getLogger(__name__)


class CassandraDriver(object):

    def __init__(self, session, table_name):
        """
        """
        self._session = session
        self._table_name = table_name

    @staticmethod
    def _extract_criteria(dict_):
        """
        DRY helper to leverage locals() safely.
        """
        return {k: dict_[k] for k in (
            'student_id',
            'course_key',
            'block_type',
            'usage_key',
            'field_name'
        )}

    @staticmethod
    def _serialize_field_value(value):
        """
        """
        return json.dumps(value)

    @staticmethod
    def _deserialize_field_value(value):
        """
        """
        return json.loads(value)

    def get_current_field_value(
            self,
            student_id,
            course_key,
            block_type,
            usage_key,
            field_name
    ):
        """
        Supports get() for the key value store
        """
        criteria = self._extract_criteria(locals())
        where = ' AND '.join(('{}=%({})s'.format(k, k) for k in criteria))
        query = "SELECT field_value FROM {} WHERE {}".format(
            self._table_name,
            where,
        )
        log.info(query)
        log.info(criteria)
        rows = list(self._session.execute(query, criteria))
        return self._deserialize_field_value(rows[0].field_value) if len(rows) else None

    def set_current_field_value(
            self,
            student_id,
            course_key,
            block_type,
            usage_key,
            field_name,
            field_value
    ):
        """
        Supports set() for the key value store
        """
        values = self._extract_criteria(locals())
        values.update({'field_value': self._serialize_field_value(field_value)})
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            self._table_name,
            ', '.join(values.keys()),
            ', '.join(('%({})s'.format(k) for k in values))
        )
        log.info(query)
        log.info(values)
        self._session.execute(query, values)

    def delete_current_field_value(
            self,
            student_id,
            course_key,
            block_type,
            usage_key,
            field_name
    ):
        """
        Supports delete() for the key value store
        """
        criteria = self._extract_criteria(locals())
        where = ' AND '.join(('{}=%({})s'.format(k, k) for k in criteria))
        self._session.execute(
            "DELETE FROM {} WHERE {}".format(
                self._table_name,
                where,
            ),
            criteria,
        )

    def get_all_submitted_problems_read_only(self, course_key):
        """
        support for grader access, providing the equivalent of
        courseware.models.StudentModule.all_submitted_problems_read_only
        """
        raise NotImplementedError("haven't hacked this one in yet!")

    def get_current_field_values(self, student_id, course_key):
        """
        support for grader access - should return a nested dictionary:
            {usage_key => {field_name: field_value}}
        for all the student's user_state coursewide.

        TODO: will this ever be a dangerously large result?  if so, should
        the interface be iterable / filterable instead?
        """
        raise NotImplementedError("haven't hacked this one in yet!")

    # TODO: need accessor method(s) for student_module history.  Not yet sure
    # what that should look like.
