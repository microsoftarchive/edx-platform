"""
This suite of tests verifies that courses exported from one modulestore can be imported into
another modulestore and the result will be identical (ignoring changes to identifiers that are
the result of being imported into a course with a different course id).

It does this by providing facilities for creating and cleaning up each of the modulestore types,
and then for each combination of modulestores, performing the sequence:
    1) use xml_importer to read a course from xml from disk into the first modulestore (called the source)
    2) use xml_exporter to dump the course from the source modulestore to disk
    3) use xml_importer to read the dumped course into a second modulestore (called the destination)
    4) Compare all modules in the source and destination modulestores to make sure that they line up

"""
import ddt
import itertools
import random
import contracts
import re
from contextlib import contextmanager, nested
from shutil import rmtree
from tempfile import mkdtemp

from xmodule.tests import CourseComparisonTest

from xmodule.modulestore.mongo.base import ModuleStoreEnum
from xmodule.modulestore.mongo.draft import DraftModuleStore
from xmodule.modulestore.mixed import MixedModuleStore
from xmodule.contentstore.mongo import MongoContentStore
from xmodule.modulestore.xml_importer import import_from_xml
from xmodule.modulestore.xml_exporter import export_to_xml
from xmodule.modulestore.split_mongo.split_draft import DraftVersioningModuleStore
from xmodule.modulestore.tests.mongo_connection import MONGO_PORT_NUM, MONGO_HOST
from xmodule.modulestore.inheritance import InheritanceMixin
from xmodule.x_module import XModuleMixin


COMMON_DOCSTORE_CONFIG = {
    'host': MONGO_HOST,
    'port': MONGO_PORT_NUM,
}


XBLOCK_MIXINS = (InheritanceMixin, XModuleMixin)


class MemoryCache(object):
    """
    This fits the metadata_inheritance_cache_subsystem interface used by
    the modulestore, and stores the data in a dictionary in memory.
    """
    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        """
        Get a key from the cache.

        Args:
            key: The key to update.
            default: The value to return if the key hasn't been set previously.
        """
        return self._data.get(key, default)

    def set(self, key, value):
        """
        Set a key in the cache.

        Args:
            key: The key to update.
            value: The value change the key to.
        """
        self._data[key] = value


class MongoModulestoreBuilder(object):
    """
    A builder class for a DraftModuleStore.
    """
    def __init__(self):
        self.doc_store_config = dict(
            db='modulestore{}'.format(random.randint(0, 10000)),
            collection='xmodule',
            **COMMON_DOCSTORE_CONFIG
        )

    def build(self, contentstore):
        return DraftModuleStore(
            contentstore,
            self.doc_store_config,
            self.fs_root,
            render_template=repr,
            branch_setting_func=lambda: ModuleStoreEnum.Branch.draft_preferred,
            metadata_inheritance_cache_subsystem=MemoryCache(),
            xblock_mixins=XBLOCK_MIXINS,
        )

    @contextmanager
    def setup(self, contentstore):
        """
        A contextmanager that returns an isolated mongo modulestore, and then deletes
        all of its data at the end of the context.

        Args:
            contentstore: The contentstore that this modulestore should use to store
                all of its assets.
        """
        # Set up a temp directory for storing filesystem content created during import
        self.fs_root = mkdtemp()

        self.build(contentstore).ensure_indexes()

        try:
            yield
        finally:
            # Delete the created database
            self.build(contentstore)._drop_database()

            # Delete the created directory on the filesystem
            rmtree(self.fs_root, ignore_errors=True)

    def __repr__(self):
        return 'MongoModulestoreBuilder()'


class VersioningModulestoreBuilder(object):
    """
    A builder class for a VersioningModuleStore.
    """
    def __init__(self):
        self.doc_store_config = dict(
            db='modulestore{}'.format(random.randint(0, 10000)),
            collection='split_module',
            **COMMON_DOCSTORE_CONFIG
        )

    def build(self, contentstore):
        return DraftVersioningModuleStore(
            contentstore,
            self.doc_store_config,
            self.fs_root,
            render_template=repr,
            xblock_mixins=XBLOCK_MIXINS,
        )

    @contextmanager
    def setup(self, contentstore):
        """
        A contextmanager that returns an isolated versioning modulestore, and then deletes
        all of its data at the end of the context.

        Args:
            contentstore: The contentstore that this modulestore should use to store
                all of its assets.
        """
        # pylint: disable=unreachable
        # Set up a temp directory for storing filesystem content created during import
        self.fs_root = mkdtemp()

        self.build(contentstore).ensure_indexes()

        try:
            yield
        finally:
            # Delete the created database
            self.build(contentstore)._drop_database()

            # Delete the created directory on the filesystem
            rmtree(self.fs_root, ignore_errors=True)

    def __repr__(self):
        return 'SplitModulestoreBuilder()'


class MixedModulestoreBuilder(object):
    """
    A builder class for a MixedModuleStore.
    """
    def __init__(self, store_builders, mappings=None):
        """
        Args:
            store_builders: A list of modulestore builder objects. These will be instantiated, in order,
                as the backing stores for the MixedModuleStore.
            mappings: Any course mappings to pass to the MixedModuleStore on instantiation.
        """
        self.store_builders = store_builders
        self.mappings = mappings or {}

    def build(self, contentstore):
        names, builders = zip(*self.store_builders)

        # Make the modulestore creation function just return the already-created modulestores
        store_iterator = (builder.build(contentstore) for builder in builders)
        create_modulestore_instance = lambda *args, **kwargs: store_iterator.next()

        # Generate a fake list of stores to give the already generated stores appropriate names
        stores = [{'NAME': name, 'ENGINE': 'This space deliberately left blank'} for name in names]

        return MixedModuleStore(
            contentstore,
            self.mappings,
            stores,
            create_modulestore_instance=create_modulestore_instance,
            xblock_mixins=XBLOCK_MIXINS,
        )

    @contextmanager
    def setup(self, contentstore):
        """
        A contextmanager that returns a mixed modulestore built on top of modulestores
        generated by other builder classes.

        Args:
            contentstore: The contentstore that this modulestore should use to store
                all of its assets.
        """
        names, generators = zip(*self.store_builders)

        with nested(*(gen.setup(contentstore) for gen in generators)):
            yield

    def __repr__(self):
        return 'MixedModulestoreBuilder({!r}, {!r})'.format(self.store_builders, self.mappings)


class MongoContentstoreBuilder(object):
    """
    A builder class for a MongoContentStore.
    """

    def __init__(self):
        self.kwargs = dict(
            db='contentstore{}'.format(random.randint(0, 10000)),
            collection='content',
            **COMMON_DOCSTORE_CONFIG
        )

    def build(self):
        return MongoContentStore(**self.kwargs)

    @contextmanager
    def setup(self):
        """
        A contextmanager that returns a MongoContentStore, and deletes its contents
        when the context closes.
        """
        self.build().ensure_indexes()

        try:
            yield
        finally:
            # Delete the created database
            self.build()._drop_database()

    def __repr__(self):
        return 'MongoContentstoreBuilder()'


MODULESTORE_SETUPS = (
#    MongoModulestoreBuilder(),
#    VersioningModulestoreBuilder(),  # FIXME LMS-11227
    MixedModulestoreBuilder([('draft', MongoModulestoreBuilder())]),
    MixedModulestoreBuilder([('split', VersioningModulestoreBuilder())]),
)
CONTENTSTORE_SETUPS = (MongoContentstoreBuilder(),)
COURSE_DATA_NAMES = (
    #'toy',
    #'manual-testing-complete',
    #'split_test_module',
    #'split_test_module_draft',
    'MITx...4.605x_2...3T2014',
)

import statprof

from pyinstrument import Profiler

@ddt.ddt
class CrossStoreXMLRoundtrip(CourseComparisonTest):
    """
    This class exists to test XML import and export between different modulestore
    classes.
    """

    def setUp(self):
        super(CrossStoreXMLRoundtrip, self).setUp()
        self.export_dir = mkdtemp()
        print self.export_dir
        #self.addCleanup(rmtree, self.export_dir, ignore_errors=True)

        # Checking contracts adds a lot of time to these tests
        contracts.disable_all()

    @ddt.data(*itertools.product(
        MODULESTORE_SETUPS,
        MODULESTORE_SETUPS,
        CONTENTSTORE_SETUPS,
        CONTENTSTORE_SETUPS,
        COURSE_DATA_NAMES,
    ))
    @ddt.unpack
    def test_round_trip(self, source_builder, dest_builder, source_content_builder, dest_content_builder, course_data_name):

        # Construct the contentstore for storing the first import
        with source_content_builder.setup():
            # Construct the modulestore for storing the first import (using the previously created contentstore)
            with source_builder.setup(source_content_builder.build()):
                # Construct the contentstore for storing the second import
                with dest_content_builder.setup():
                    # Construct the modulestore for storing the second import (using the second contentstore)
                    with dest_builder.setup(dest_content_builder.build()):
                        # Use 'course' as the name to minimize the differences between split and mongo key formats
                        source_course_key = source_builder.build(source_content_builder.build()).make_course_key('a', 'course', 'course')
                        dest_course_key = dest_builder.build(dest_content_builder.build()).make_course_key('a', 'course', 'course')

                        source_name = re.sub('\W+', '-', unicode(source_builder))
                        dest_name = re.sub('\W+', '-', unicode(dest_builder))
                        print "Import into", source_builder
                        with profile('import_source_{}_{}.html'.format(source_name, dest_name)):
                            import_from_xml(
                                source_builder.build(source_content_builder.build()),
                                'test_user',
                                #'common/test/data',
                                '../data-prod-export/coursedump',
                                course_dirs=[course_data_name],
                                static_content_store=source_content_builder.build(),
                                target_course_id=source_course_key,
                                create_new_course_if_not_present=True,
                                do_import_static=False,
                            )

                        print "Export from", source_builder
                        with profile('export_source_{}_{}.html'.format(source_name, dest_name)):
                            export_to_xml(
                                source_builder.build(source_content_builder.build()),
                                source_content_builder.build(),
                                source_course_key,
                                self.export_dir,
                                'exported_source_course',
                            )

                        print "Import into", dest_builder
                        with profile('import_dest_{}_{}.html'.format(source_name, dest_name)):
                            import_from_xml(
                                dest_builder.build(dest_content_builder.build()),
                                'test_user',
                                self.export_dir,
                                course_dirs=['exported_source_course'],
                                static_content_store=dest_content_builder.build(),
                                target_course_id=dest_course_key,
                                create_new_course_if_not_present=True,
                                do_import_static=False,
                            )

                        print "Export from", dest_builder
                        with profile('export_dest_{}_{}.html'.format(source_name, dest_name)):
                            export_to_xml(
                                dest_builder.build(dest_content_builder.build()),
                                dest_content_builder.build(),
                                dest_course_key,
                                self.export_dir,
                                'exported_dest_course',
                            )

                        # print "Compare", source_builder, dest_builder
                        # with profile('compare_{}_{}.html'.format(source_name, dest_name)):
                        #     self.exclude_field(None, 'wiki_slug')
                        #     self.exclude_field(None, 'xml_attributes')
                        #     self.exclude_field(None, 'parent')
                        #     self.exclude_field(None, 'static_asset_path')
                        #     self.ignore_asset_key('_id')
                        #     self.ignore_asset_key('uploadDate')
                        #     self.ignore_asset_key('content_son')
                        #     self.ignore_asset_key('thumbnail_location')

                        #     self.assertCoursesEqual(
                        #         source_builder.build(source_content_builder.build()),
                        #         source_course_key,
                        #         dest_builder.build(dest_content_builder.build()),
                        #         dest_course_key,
                        #     )

                        #     self.assertAssetsEqual(
                        #         source_content_builder.build(),
                        #         source_course_key,
                        #         dest_content_builder.build(),
                        #         dest_course_key,
                        #     )


@contextmanager
def profile(filename):
    profiler = Profiler()
    profiler.start()

    try:
        yield
    finally:
        profiler.stop()

        with open(filename, 'w') as file:
            print >> file, profiler.output_html()
