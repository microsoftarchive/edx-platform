""" Django REST Framework Serializers """

from django.core.urlresolvers import reverse
from rest_framework import serializers

from courseware.courses import course_image_url


# pylint: disable=invalid-name
class CourseSerializer(serializers.Serializer):
    """ Serializer for Courses """
    id = serializers.CharField()
    name = serializers.CharField(source='display_name')
    category = serializers.CharField()
    org = serializers.SerializerMethodField('get_org')
    run = serializers.SerializerMethodField('get_run')
    course = serializers.SerializerMethodField('get_course')
    uri = serializers.SerializerMethodField('get_uri')
    image_url = serializers.SerializerMethodField('get_image_url')
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def get_org(self, course):
        """ Gets the course org """
        return course.location.org

    def get_run(self, course):
        """ Gets the course run """
        return course.location.run

    def get_course(self, course):
        """ Gets the course """
        return course.location.course

    def get_uri(self, course):
        """ Builds course detail uri """
        # pylint: disable=no-member
        request = self.context['request']
        return request.build_absolute_uri(reverse('course_structure_api_v0:detail', kwargs={'course_id': course.id}))

    def get_image_url(self, course):
        """ Get the course image URL """
        return course_image_url(course)


class GradingPolicySerializer(serializers.Serializer):
    """ Serializer for course grading policy. """
    assignment_type = serializers.CharField(source='type')
    count = serializers.IntegerField(source='min_count')
    dropped = serializers.IntegerField(source='drop_count')
    weight = serializers.FloatField()


class CourseStructureSerializer(serializers.Serializer):
    root = serializers.CharField(source='root')
    blocks = serializers.SerializerMethodField('get_blocks')

    def get_blocks(self, structure):
        serialized = {}

        for key, block in structure.blocks.iteritems():
            # Ensure graded is always a boolean value
            block.graded = block.graded or False
            serialized[key] = block.__dict__

        return serialized
