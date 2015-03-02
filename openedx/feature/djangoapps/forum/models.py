"""
model interfaces to the database of forum content.
"""

import datetime

from bson.objectid import ObjectId
from mongoengine import Document, EmbeddedDocument, Q
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    DictField,
    EmbeddedDocumentField,
    IntField,
    ListField,
    ReferenceField,
    StringField
)


class ForumContent(Document):
    """
    Base class for attributes / behaviors shared by both Threads and Comments.
    """

    meta = {'allow_inheritance': True, 'collection': 'contents'}

    abuse_flaggers = ListField()
    historical_abuse_flaggers = ListField() #preserve abuse flaggers after a moderator unflags)
    anonymous = BooleanField(default=False)
    anonymous_to_peers = BooleanField(default=False)
    at_position_list = ListField()
    author_id = StringField()
    author_username = StringField()
    body = StringField()
    commentable_id = StringField()
    course_id = StringField()
    updated_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    visible = BooleanField(default=True)
    votes = DictField()

    # needed?
    @property
    def author(self):
        print ForumUser.objects(external_id=self.author_id)._query
        return ForumUser.objects.get(external_id=self.author_id)

    # from cs Content model - move to serializer
    def author_with_anonymity(self, attr=None, attr_when_anonymous=None):
        if not attr:
            if self.anonymous or self.anonymous_to_peers:
                return None
            else:
                return self.author
        else:
            if self.anonymous or self.anonymous_to_peers:
                return attr_when_anonymous
            else:
                return getattr(self.author, attr)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        if not self.author_username:
            self.author_username = self.author.username
        return super(ForumContent, self).save(*args, **kwargs)


class ForumThread(ForumContent):

    closed = BooleanField(default=False)
    comment_count = IntField(default=0)
    group_id = IntField()
    last_activity_at = DateTimeField(default=datetime.datetime.utcnow)
    pinned = BooleanField(default=False)
    thread_type = StringField(default="discussion")
    #enumerize :thread_type, in: [:question, :discussion]
    title = StringField()

    #index({author_id: 1, course_id: 1})
    #belongs_to :author, class_name: "User", inverse_of: :comment_threads, index: true#, autosave: true
    #has_many :comments, dependent: :destroy#, autosave: true# Use destroy to envoke callback on the top-level comments TODO async
    #has_many :activities, autosave: true
    #attr_accessible :title, :body, :course_id, :commentable_id, :anonymous, :anonymous_to_peers, :closed, :thread_type
    #validates_presence_of :thread_type
    #validates_presence_of :title
    #validates_presence_of :body
    #validates_presence_of :course_id # do we really need this?
    #validates_presence_of :commentable_id
    #validates_presence_of :author, autosave: false
    #before_create :set_last_activity_at
    #before_update :set_last_activity_at, :unless => lambda { closed_changed? }
    #after_update :clear_endorsements
    #before_destroy :destroy_subscriptions
    #scope :active_since, ->(from_time) { where(:last_activity_at => {:$gte => from_time}) }
    #def root_comments
    #    Comment.roots.where(comment_thread_id: self.id)
    #def commentable
    #    Commentable.find(commentable_id)
    #def subscriptions
    #    Subscription.where(source_id: id.to_s, source_type: self.class.to_s)
    #def subscribers
    #    subscriptions.map(&:subscriber)
    #def endorsed
    #    comments.where(endorsed: true).exists?
    #  # GET /api/v1/threads/{id}
    #
    #  begin
    #    thread = CommentThread.find(thread_id)
    #  rescue Mongoid::Errors::DocumentNotFound
    #    error 404, [t(:requested_object_not_found)].to_json
    #  end
    #
    #  if params["user_id"] and bool_mark_as_read
    #    user = User.only([:id, :username, :read_states]).find_by(external_id: params["user_id"])
    #    user.mark_as_read(thread) if user
    #  end
    #
    #  presenter = ThreadPresenter.factory(thread, user || nil)
    #  if params.has_key?("resp_skip")
    #    unless (resp_skip = Integer(params["resp_skip"]) rescue nil) && resp_skip >= 0
    #      error 400, [t(:param_must_be_a_non_negative_number, :param => 'resp_skip')].to_json
    #    end
    #  else
    #    resp_skip = 0
    #  end
    #  if params["resp_limit"]
    #    unless (resp_limit = Integer(params["resp_limit"]) rescue nil) && resp_limit >= 0
    #      error 400, [t(:param_must_be_a_number_greater_than_zero, :param => 'resp_limit')].to_json
    #    end
    #  else
    #    resp_limit = nil
    #  end
    #  presenter.to_hash(true, resp_skip, resp_limit).to_json

    @property
    def comment_thread_id(self):
        #so that we can use the comment thread id as a common attribute for flagging
        return self.id

    def set_last_activity_at(self):
        self.last_activity_at = datetime.datetime.utcnow()

    def clear_endorsements(self):
        #if self.thread_type_changed?
        # We use 'set' instead of 'update_attributes' because the Comment model has a 'before_update' callback that sets
        # the last activity time on the thread. Therefore the callbacks would be mutually recursive and we end up with a
        # 'SystemStackError'. The 'set' method skips callbacks and therefore bypasses this issue.
        for comment in self.comments:
            comment.endorsed = False
            comment.endorsement = None


class ForumComment(ForumContent):

    #include Mongoid::Tree
    #include Mongoid::Timestamps
    #include Mongoid::MagicCounterCache

    #voteable self, :up => +1, :down => -1

    # this may not be right
    comment_thread_id = ReferenceField('ForumThread', dbref=False)
    endorsed = BooleanField(default=False)
    endorsement = DictField()
    parent_id = ReferenceField('ForumComment')
    parent_ids = ListField(ReferenceField('ForumComment'))
    sk = StringField(default=None)

    #index({author_id: 1, course_id: 1})
    #index({_type: 1, comment_thread_id: 1, author_id: 1, updated_at: 1})

    #before_save :set_sk
    #def set_sk(self):
    #    # this attribute is explicitly write-once
    #    if self.sk is None:

    def save(self, *args, **kwargs):
        if not self.sk:
            self.sk = "-".join([str(oid) for oid in (self.parent_ids + [self.id])])
        return super(ForumComment, self).save(*args, **kwargs)


    #belongs_to :comment_thread, index: true
    #belongs_to :author, class_name: "User", index: true

    #attr_accessible :body, :course_id, :anonymous, :anonymous_to_peers, :endorsed, :endorsement

    #validates_presence_of :comment_thread, autosave: false
    #validates_presence_of :body
    #validates_presence_of :course_id
    #validates_presence_of :author, autosave: false

    #counter_cache :comment_thread

    #before_destroy :destroy_children # TODO async

    #before_create :set_thread_last_activity_at
    #before_update :set_thread_last_activity_at

    @classmethod
    def hash_tree(cls, nodes):
        #nodes.map{|node, sub_nodes| node.to_hash.merge("children" => hash_tree(sub_nodes).compact)}
        raise NotImplementedError

    # This should really go somewhere else, but sticking it here for now. This is
    # used to flatten out the subtree fetched by calling self.subtree. This is
    # equivalent to calling descendants_and_self; however, calling
    # descendants_and_self and subtree both is very inefficient. It's cheaper to
    # just flatten out the subtree, and simpler than duplicating the code that
    # actually creates the subtree.
    @classmethod
    def flatten_subtree(cls, x):
        raise NotImplementedError
        #if x.is_a? Array
        #    x.flatten.map{|y| self.flatten_subtree(y)}
        #elif x.is_a? Hash
        #    x.to_a.map{|y| self.flatten_subtree(y)}.flatten
        #else
        #    x


    def to_dict(self, params={}):
        #sort_by_parent_and_time = Proc.new do |x, y|
        #arr_cmp = x.parent_ids.map(&:to_s) <=> y.parent_ids.map(&:to_s)
        #if arr_cmp != 0
        #arr_cmp
        #else
        #x.created_at <=> y.created_at
        #
        #if params[:recursive]
        ## TODO: remove and reuse the new hierarchical sort keys if possible
        #subtree_hash = subtree(sort: sort_by_parent_and_time)
        #self.class.hash_tree(subtree_hash).first
        #else
        hash = self.to_mongo()
        hash = {k:hash.get(k) for k in "body course_id endorsed endorsement anonymous anonymous_to_peers created_at updated_at at_position_list".split(' ')}
        #as_document.slice(*%w[body course_id endorsed endorsement anonymous anonymous_to_peers created_at updated_at at_position_list])
        hash.update({
            "id": str(self.id),
            "user_id": self.author_id,
            "username": self.author_username,
            "depth": 1,   # ??
            #.merge("closed" => comment_thread is None ? false : comment_thread.closed) # ditto
            "closed": False,
            #.merge("thread_id" => comment_thread_id)
            "thread_id": str(self.comment_thread_id),
            #.merge("commentable_id" => comment_thread is None ? None : comment_thread.commentable_id) # ditto
            "commentable_id": None,  # ?
            #.merge("votes" => votes.slice(*%w[count up_count down_count point]))
            "votes": {"up" : [ ], "down" : [ ], "up_count" : 0, "down_count" : 0, "count" : 0, "point" : 0},
            #.merge("abuse_flaggers" => abuse_flaggers)
            "abuse_flaggers": [],
            #.merge("type" => "comment")
            "type": "comment",
        })
        #.merge("user_id" => author_id)
        #.merge("username" => author_username)
        #.merge("depth" => depth)
        #.merge("closed" => comment_thread is None ? false : comment_thread.closed) # ditto
        #.merge("thread_id" => comment_thread_id)
        #.merge("commentable_id" => comment_thread is None ? None : comment_thread.commentable_id) # ditto
        #.merge("votes" => votes.slice(*%w[count up_count down_count point]))
        #.merge("abuse_flaggers" => abuse_flaggers)
        #.merge("type" => "comment")
        return hash

    @property
    def thread(self):
        return ForumThread.objects.get(id=self.comment_thread_id)

    @classmethod
    def by_date_range_and_thread_ids(cls, from_when, to_when, thread_ids):
        raise NotImplementedError
        #return all content between from_when and to_when
        #self.where(:created_at.gte => (from_when)).where(:created_at.lte => (to_when)).
        #where(:comment_thread_id.in => thread_ids)

    def set_thread_last_activity_at(self):
        raise NotImplementedError
        #self.comment_thread.update_attributes!(last_activity_at: Time.now.utc)



class ForumUser(Document):

    meta = {'allow_inheritance': False, 'collection': 'users'}
    #include Mongo::Voter

    id = StringField(primary_key=True)
    external_id = StringField()
    # the above two need to be kept in sync
    username = StringField()
    default_sort_key = StringField(default="date")

    #comments = ListField(ReferenceField('ForumComment'))
    #threads = ListField(ReferenceField('ForumThread'))
    read_states = ListField(EmbeddedDocumentField('ForumReadState'))
    #has_many :comments, inverse_of: :author
    #has_many :comment_threads, inverse_of: :author
    #has_many :activities, class_name: "Notification", inverse_of: :actor
    #has_and_belongs_to_many :notifications, inverse_of: :receivers

    #validates_presence_of :external_id
    #validates_presence_of :username
    #validates_uniqueness_of :external_id
    #validates_uniqueness_of :username

    #index( {external_id: 1}, {unique: true, background: true} )

    def follow(self, thread):
        """
        """
        #if source._id == self._id and source.class == self.class
        #  raise ArgumentError, "Cannot follow oneself"
        #else
        #  Subscription.find_or_create_by(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s)
        #end
        #assert isinstance(thread, Thread)
        ForumSubscription.objects.get_or_create(
            subscriber_id=str(self.id),
            source_id=str(thread.id),
            source_type="Thread"
        )

    def unfollow(self, thread):
        """
        """
        # subscription = Subscription.where(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s).first
        # subscription.destroy if subscription
        # subscription
        ForumSubscription.objects(
            subscriber_id=str(self.id),
            source_id=str(thread.id),
            source_type="Thread",
        ).delete()

    @property
    def subscriptions_as_source(self):
        raise NotImplementedError
        #Subscription.where(source_id: id.to_s, source_type: self.class.to_s)

    @property
    def subscribed_thread_ids(self):
        #raise NotImplementedError
        subs = ForumSubscription.objects(
            subscriber_id=self.id,
            source_type="Thread"
        )
        return [doc.source_id for doc in subs]

    @property
    def subscribed_threads(self):
        raise NotImplementedError
        #CommentThread.in({"_id" => subscribed_thread_ids})

    @property
    def upvoted_ids(self):
        #raise NotImplementedError
        return []
        #Content.up_voted_by(self).map(&:id)


    @property
    def downvoted_ids(self):
        #raise NotImplementedError
        return []
        #Content.down_voted_by(self).map(&:id)


    @property
    def followers(self):
        raise NotImplementedError
        #subscriptions_as_source.map(&:subscriber)


    def subscribe(self, source):
        raise NotImplementedError
        #if source._id == self._id and source.class == self.class
        #    raise ArgumentError, "Cannot follow oneself"
        #else
        #    Subscription.find_or_create_by(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s)

    def unsubscribe(self, source):
        raise NotImplementedError
        #subscription = Subscription.where(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s).first
        #subscription.destroy if subscription
        #subscription

    def mark_as_read(self, thread):
        raise NotImplementedError
        #read_state = read_states.find_or_create_by(course_id: thread.course_id)
        #read_state.last_read_times[thread.id.to_s] = Time.now.utc
        #read_state.save


class ForumReadState(EmbeddedDocument):

    course_id = StringField()
    last_read_times = DictField(default={})
    #embedded_in :user

    #validates :course_id, uniqueness: true, presence: true

    def to_dict(self):
        return self.to_mongo().to_dict()


class ForumSubscription(Document):
    #include Mongoid::Timestamps

    meta = {'collection': 'subscriptions'}

    subscriber_id = StringField()
    source_id = StringField()
    source_type = StringField()

    def to_dict(self):
        return {
            "subscriber_id": self.subscriber_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
        }

    @property
    def subscriber(self):
        return ForumUser.objects.get(self.subscriber_id)

    @property
    def source(self):
        return {
            "Thread": ForumThread,
            "Comment": ForumComment,
        }[self.source_type].get(self.source_id)



# FIXME only set up for devstack atm.
from mongoengine import connect
cx = connect('cs_comments_service_development')
