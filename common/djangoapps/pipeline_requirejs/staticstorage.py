"""
:class:`pipeline_requirejs.staticstorage.OptimizedCachedRequireJsStorage`
"""

import os
import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from pipeline.storage import PipelineCachedStorage
from require.storage import OptimizedFilesMixin


class OptimizedCachedRequireJsStorage(OptimizedFilesMixin, PipelineCachedStorage):
    """
    Custom storage backend that is used by Django-require.
    """
    def __init__(self, *args, **kwargs):
        self.generate_build_file()
        super(OptimizedCachedRequireJsStorage, self).__init__(*args, **kwargs)

    def generate_build_file(self):
        """
        Generates build file for r.js.
        """
        modules_path = os.path.join(settings.REQUIRE_STATIC_DIR, settings.REQUIRE_PAGE_FACTORIES_ROOT)

        if not settings.REQUIRE_BUILD_PROFILES_ROOT:
            raise ImproperlyConfigured("Your REQUIRE_BUILD_PROFILES_ROOT setting needs to be defined.")

        if not os.path.exists(settings.REQUIRE_BUILD_PROFILES_ROOT):
            os.makedirs(settings.REQUIRE_BUILD_PROFILES_ROOT)

        build_file = os.path.join(settings.REQUIRE_BUILD_PROFILES_ROOT, settings.REQUIRE_BUILD_PROFILE)
        modules, common_dependencies = self.get_modules(modules_path)
        content = render_to_string("build.js", {
            "modules": json.dumps(modules),
            "common": json.dumps(common_dependencies),
        })

        with open(build_file, 'w+') as build:
            build.write(content)

    def get_filename(self, name):
        """
        Returns a filename without extension.
        """
        return os.path.splitext(name)[0]

    def get_relative_path(self, root, name):
        """
        Returns a path to the file relative to REQUIRE_STATIC_DIR.

        Example:
            ..cms/static/js/factories/filename.js -> js/factories/filename
        """
        return os.path.join(root.replace((settings.REQUIRE_STATIC_DIR + os.path.sep), ""), self.get_filename(name))

    def get_modules(self, path):
        """
        Returns a tuple with lists of general modules and common dependencies.
        """
        modules = []
        common = []
        for root, dirs, files in os.walk(path):  # pylint: disable=unused-variable
            for name in files:
                relative_path = self.get_relative_path(root, name)
                if relative_path in settings.REQUIRE_COMMON_DEPENDENCIES:
                    common.append(relative_path)
                else:
                    modules.append(relative_path)
        return modules, common
