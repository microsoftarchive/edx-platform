"""
:class:`pipeline_requirejs.finders.PipelineRequirejsFinder`
"""

import os
from django.core.exceptions import ImproperlyConfigured
from staticfiles.finders import BaseFinder
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.utils._os import safe_join
from staticfiles import utils, storage


class PipelineRequirejsFinder(BaseFinder):
    """
    A build profile files finder that uses the ``REQUIRE_BUILD_PROFILES_ROOT`` setting
    to locate files.
    """
    def __init__(self, apps=None, *args, **kwargs):
        # List of locations with static files
        self.locations = []
        # Maps dir paths to an appropriate storage instance
        self.storages = SortedDict()
        if not settings.REQUIRE_BUILD_PROFILES_ROOT:
            raise ImproperlyConfigured("Your REQUIRE_BUILD_PROFILES_ROOT setting needs to be defined.")

        root = settings.REQUIRE_BUILD_PROFILES_ROOT
        if root not in self.locations:
            self.locations.append(root)

        for root in self.locations:
            filesystem_storage = storage.TimeAwareFileSystemStorage(location=root)
            self.storages[root] = filesystem_storage

    def list(self, ignore_patterns):
        """
        List all files in all app storages.
        """
        for storage in self.storages.itervalues():
            if storage.exists(''):  # check if storage location exists
                for path in utils.get_files(storage, ignore_patterns):
                    yield path, storage

    def find(self, path, all=False):
        """
        Looks for files in the REQUIRE_BUILD_PROFILES_ROOT directory.
        """
        matches = []
        for root in self.locations:
            matched_path = self.find_location(root, path)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path):
        """
        Finds a requested static file in a location, returning the found
        absolute path (or ``None`` if no match).
        """
        path = safe_join(root, path)
        if os.path.exists(path):
            return path
