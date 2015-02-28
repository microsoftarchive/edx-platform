import datetime
import unittest

from lms.djangoapps.django_comment_client.base.models import *

class ModelsTestCase(unittest.TestCase):
    pass

class ThreadTestCase(ModelsTestCase):

    maxDiff = None

    def test_any(self):

        author, __ = User.objects.get_or_create(id="xyz", external_id="xyz")

        thread_data = dict(
            author_id=author.id,
            thread_type="discussion",
            #comment_count=123,
            title="title",
            body="body",
            course_id="course_id",
            commentable_id="commentable_id",
            anonymous=False,
            anonymous_to_peers=False,
            closed=False,
            #at_position_list=[],  # kill me
            #last_activity_at=datetime.datetime.now(),
            group_id=9,
            #pinned=True
        )

        thread = Thread(**thread_data)
        thread.save()
        thread_id = thread.id
        other_thread = Thread.objects.get(id=thread_id)
        self.assertEqual(other_thread, thread)
        self.assertEqual(other_thread.to_dict(), thread.to_dict())

if __name__ == '__main__':
    unittest.main()
