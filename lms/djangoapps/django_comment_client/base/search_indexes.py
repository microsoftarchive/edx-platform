import datetime

from haystack import indexes

from .models import Comment, Thread

class ThreadIndex(indexes.SearchIndex, indexes.Indexable):

    #indexes :title, type: :string, analyzer: :english, boost: 5.0, stored: true, term_vector: :with_positions_offsets
    title = indexes.CharField(boost=5.0, stored=True)
    #indexes :body, type: :string, analyzer: :english, stored: true, term_vector: :with_positions_offsets
    body = indexes.CharField(stored=True)
    #indexes :created_at, type: :date, included_in_all: false
    created_at = indexes.DateTimeField()
    #indexes :updated_at, type: :date, included_in_all: false
    updated_at = indexes.DateTimeField()
    #indexes :last_activity_at, type: :date, included_in_all: false
    last_activity_at = indexes.DateTimeField()

    #indexes :comment_count, type: :integer, included_in_all: false
    comment_count = indexes.IntegerField()
    #indexes :votes_point, type: :integer, as: 'votes_point', included_in_all: false
    votes_point = indexes.IntegerField()
    #indexes :course_id, type: :string, index: :not_analyzed, included_in_all: false
    course_id = indexes.CharField()
    #indexes :commentable_id, type: :string, index: :not_analyzed, included_in_all: false
    commentable_id = indexes.CharField()
    #indexes :author_id, type: :string, as: 'author_id', index: :not_analyzed, included_in_all: false
    author_id = indexes.CharField()
    #indexes :group_id, type: :integer, as: 'group_id', index: :not_analyzed, included_in_all: false
    group_id = indexes.IntegerField()
    #indexes :id,         :index    => :not_analyzed

    #indexes :thread_id, :analyzer => :keyword, :as => "_id"
    thread_id = indexes.CharField()

    def get_model(self):
        return Thread

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())


class CommentIndex(indexes.SearchIndex, indexes.Indexable):

    #indexes :body, type: :string, analyzer: :english, stored: true, term_vector: :with_positions_offsets
    body = indexes.CharField(stored=True)
    #indexes :course_id, type: :string, index: :not_analyzed, included_in_all: false
    course_id = indexes.CharField()
    #indexes :comment_thread_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'comment_thread_id'
    comment_thread_id = indexes.CharField()
    #indexes :commentable_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'commentable_id'
    commentable_id = indexes.CharField()
    #indexes :group_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'group_id'
    group_id = indexes.IntegerField()
    #indexes :created_at, type: :date, included_in_all: false
    created_at = indexes.DateTimeField()
    #indexes :updated_at, type: :date, included_in_all: false
    updated_at = indexes.DateTimeField()

    def get_model(self):
        return Comment

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())

