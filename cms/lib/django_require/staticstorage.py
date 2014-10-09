from pipeline.storage import PipelineStorage
from require.storage import OptimizedFilesMixin


class OptimizedCachedRequireJSStorage(OptimizedFilesMixin, PipelineStorage):
    """
    Custom storage backend that is used by Django-require.
    """
    pass
