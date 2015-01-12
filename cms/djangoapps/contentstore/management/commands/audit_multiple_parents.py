"""
Script for finding courses with modules with multiple parents
"""
from collections import Counter

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

        print u"\nLooking through courses for modules with dangling pointers...\n"
        for course_key in split_course_keys:

            children_parent_map = self.find_dags(split_store, course_key)

            if not children_parent_map:
                continue
            print u"Course {course_key} has the following modules with dangling pointers:".format(course_key=unicode(course_key))
            for pointer, parents in children_parent_map.iteritems():
                print u"pointer: {type} {id}".format(type=pointer.type, id=pointer.id)
                print u"parents:"
                for parent in parents:
                    print u"\t{type} {id}".format(type=parent.type, id=parent.id)
            print "\n"

        print u"Done"

    def find_dags(self, store, course_locator):
        """
        Find blocks in a course that have multiple parents
        """
        branch = ModuleStoreEnum.RevisionOption.draft_only
        structure = store._lookup_course(
            store._map_revision_to_branch(course_locator, branch)
        ).structure

        children_list = []
        for block_id, block in structure['blocks'].iteritems():
            if 'fields' in block and 'children' in block['fields']:
                for child_id in block['fields']['children']:
                    children_list.append(child_id)

        child_counter = Counter(children_list)

        children_with_multiple_parents = []
        for child, count in child_counter.iteritems():
            if count > 1:
                children_with_multiple_parents.append(child)

        children_parent_map = {}
        for child in children_with_multiple_parents:
            children_parent_map[child] = []
            for parent in store._get_parents_from_structure(child, structure):
                children_parent_map[child].append(parent)

        return children_parent_map
