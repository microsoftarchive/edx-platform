from pipeline.storage import PipelineStorage
from require.storage import OptimizedFilesMixin


class OptimizedCachedRequireJSStorage(OptimizedFilesMixin, PipelineStorage):
    pass
