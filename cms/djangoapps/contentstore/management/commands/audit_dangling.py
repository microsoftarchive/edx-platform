"""
Script for finding courses with modules with multiple parents
"""
from collections import defaultdict

from django.core.management.base import BaseCommand
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum


class Command(BaseCommand):
    """Find modules in courses with pointers to the same child"""
    help = "Find courses with modules with multiple parents"

    def handle(self, *args, **options):
        "Execute the command"

        # for now only support on split mongo
        split_store = modulestore()._get_modulestore_by_type(ModuleStoreEnum.Type.split)

        split_course_keys = [course.id for course in split_store.get_courses()]

        print u"\nLooking through courses for dangling references...\n"
        total_courses = 0
        for course_key in split_course_keys:

            module_reference_dict = self.find_modules_with_dangling_references(split_store, course_key)

            if not module_reference_dict:
                continue
            total_courses += 1
            print u"Course {course_key} has the following modules with dangling references:".format(course_key=unicode(course_key))
            for module, references in module_reference_dict.iteritems():
                print u"module: {type} {id}".format(type=module.type, id=module.id)
                print u"references:"
                for reference in references:
                    print u"\t{type} {id}".format(type=reference.type, id=reference.id)
            print "\n"

        print u"Total of {} courses with modules with dangling references".format(total_courses)
        print u"Done"

    def find_modules_with_dangling_references(self, store, course_locator):
        """
        Find blocks in a course that have multiple parents
        """
        branch = ModuleStoreEnum.RevisionOption.draft_only
        structure = store._lookup_course(
            store._map_revision_to_branch(course_locator, branch)
        ).structure


        module_reference_dict = defaultdict(list)
        for block_id, block in structure['blocks'].iteritems():
            if 'fields' in block and 'children' in block['fields']:
                for child_id in block['fields']['children']:
                    if child_id not in  structure['blocks'].keys():
                        module_reference_dict[block_id].append(child_id)

        return module_reference_dict
