import mongoengine

class Content(mongoengine.Document):

  include Mongoid::Document
  include Mongo::Voteable

  field :visible, type: Boolean, default: true
  field :abuse_flaggers, type: Array, default: []
  field :historical_abuse_flaggers, type: Array, default: [] #preserve abuse flaggers after a moderator unflags
  field :author_username, type: String, default: nil

  index({_type: 1, course_id: 1, pinned: -1, created_at: -1 }, {background: true} )
  index({_type: 1, course_id: 1, pinned: -1, comment_count: -1, created_at: -1}, {background: true})
  index({_type: 1, course_id: 1, pinned: -1, "votes.point" => -1, created_at: -1}, {background: true})

  index({comment_thread_id: 1, sk: 1}, {sparse: true})
  index({comment_thread_id: 1, endorsed: 1}, {sparse: true})
  index({commentable_id: 1}, {sparse: true, background: true})

  ES_INDEX_NAME = 'content'

  def self.put_search_index_mapping(idx=nil)
    idx ||= self.tire.index
    success = idx.mapping(self.tire.document_type, {:properties => self.tire.mapping})
    unless success
      logger.warn "WARNING! could not apply search index mapping for #{self.name}"
    end
  end

  before_save :set_username
  def set_username
    # avoid having to look this attribute up later, since it does not change
    self.author_username = author.username
  end

  def author_with_anonymity(attr=nil, attr_when_anonymous=nil)
    if not attr
      (anonymous || anonymous_to_peers) ? nil : author
    else
      (anonymous || anonymous_to_peers) ? attr_when_anonymous : author.send(attr)
    end
  end


class Thread(Content):

  include Mongoid::Timestamps
  extend Enumerize

  voteable self, :up => +1, :down => -1

  field :thread_type, type: String, default: :discussion
  enumerize :thread_type, in: [:question, :discussion]
  field :comment_count, type: Integer, default: 0
  field :title, type: String
  field :body, type: String
  field :course_id, type: String
  field :commentable_id, type: String
  field :anonymous, type: Boolean, default: false
  field :anonymous_to_peers, type: Boolean, default: false
  field :closed, type: Boolean, default: false
  field :at_position_list, type: Array, default: []
  field :last_activity_at, type: Time
  field :group_id, type: Integer
  field :pinned, type: Boolean

  index({author_id: 1, course_id: 1})

  include Tire::Model::Search
  include Tire::Model::Callbacks

  index_name Content::ES_INDEX_NAME

  mapping do
    indexes :title, type: :string, analyzer: :english, boost: 5.0, stored: true, term_vector: :with_positions_offsets
    indexes :body, type: :string, analyzer: :english, stored: true, term_vector: :with_positions_offsets
    indexes :created_at, type: :date, included_in_all: false
    indexes :updated_at, type: :date, included_in_all: false
    indexes :last_activity_at, type: :date, included_in_all: false

    indexes :comment_count, type: :integer, included_in_all: false
    indexes :votes_point, type: :integer, as: 'votes_point', included_in_all: false

    indexes :course_id, type: :string, index: :not_analyzed, included_in_all: false
    indexes :commentable_id, type: :string, index: :not_analyzed, included_in_all: false
    indexes :author_id, type: :string, as: 'author_id', index: :not_analyzed, included_in_all: false
    indexes :group_id, type: :integer, as: 'group_id', index: :not_analyzed, included_in_all: false
    indexes :id,         :index    => :not_analyzed
    indexes :thread_id, :analyzer => :keyword, :as => "_id"
  end

  belongs_to :author, class_name: "User", inverse_of: :comment_threads, index: true#, autosave: true
  has_many :comments, dependent: :destroy#, autosave: true# Use destroy to envoke callback on the top-level comments TODO async
  has_many :activities, autosave: true

  attr_accessible :title, :body, :course_id, :commentable_id, :anonymous, :anonymous_to_peers, :closed, :thread_type

  validates_presence_of :thread_type
  validates_presence_of :title
  validates_presence_of :body
  validates_presence_of :course_id # do we really need this?
  validates_presence_of :commentable_id
  validates_presence_of :author, autosave: false

  before_create :set_last_activity_at
  before_update :set_last_activity_at, :unless => lambda { closed_changed? }
  after_update :clear_endorsements

  before_destroy :destroy_subscriptions

  scope :active_since, ->(from_time) { where(:last_activity_at => {:$gte => from_time}) }

  def root_comments
    Comment.roots.where(comment_thread_id: self.id)
  end

  def commentable
    Commentable.find(commentable_id)
  end

  def subscriptions
    Subscription.where(source_id: id.to_s, source_type: self.class.to_s)
  end

  def subscribers
    subscriptions.map(&:subscriber)
  end

  def endorsed?
    comments.where(endorsed: true).exists?
  end

  def to_hash(params={})
    as_document.slice(*%w[thread_type title body course_id anonymous anonymous_to_peers commentable_id created_at updated_at at_position_list closed])
                     .merge("id" => _id, "user_id" => author_id,
                            "username" => author_username,
                            "votes" => votes.slice(*%w[count up_count down_count point]),
                            "abuse_flaggers" => abuse_flaggers,
                            "tags" => [],
                            "type" => "thread",
                            "group_id" => group_id,
                            "pinned" => pinned?,
                            "comments_count" => comment_count)

  end

  def comment_thread_id
    #so that we can use the comment thread id as a common attribute for flagging
    self.id
  end

  def set_last_activity_at
    self.last_activity_at = Time.now.utc unless last_activity_at_changed?
  end

  def clear_endorsements
    if self.thread_type_changed?
      # We use 'set' instead of 'update_attributes' because the Comment model has a 'before_update' callback that sets
      # the last activity time on the thread. Therefore the callbacks would be mutually recursive and we end up with a
      # 'SystemStackError'. The 'set' method skips callbacks and therefore bypasses this issue.
      self.comments.each do |comment|
        comment.set :endorsed, false
        comment.set :endorsement, nil
      end
    end
  end


class Comment(Content):

  include Mongoid::Tree
  include Mongoid::Timestamps
  include Mongoid::MagicCounterCache

  voteable self, :up => +1, :down => -1

  field :course_id, type: String
  field :body, type: String
  field :endorsed, type: Boolean, default: false
  field :endorsement, type: Hash
  field :anonymous, type: Boolean, default: false
  field :anonymous_to_peers, type: Boolean, default: false
  field :at_position_list, type: Array, default: []

  index({author_id: 1, course_id: 1})
  index({_type: 1, comment_thread_id: 1, author_id: 1, updated_at: 1})

  field :sk, type: String, default: nil
  before_save :set_sk
  def set_sk()
    # this attribute is explicitly write-once
    if self.sk.nil?
      self.sk = (self.parent_ids.dup << self.id).join("-")
    end
  end

  include Tire::Model::Search
  include Tire::Model::Callbacks

  index_name Content::ES_INDEX_NAME

  mapping do
    indexes :body, type: :string, analyzer: :english, stored: true, term_vector: :with_positions_offsets
    indexes :course_id, type: :string, index: :not_analyzed, included_in_all: false
    indexes :comment_thread_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'comment_thread_id'
    indexes :commentable_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'commentable_id'
    indexes :group_id, type: :string, index: :not_analyzed, included_in_all: false, as: 'group_id'
    indexes :created_at, type: :date, included_in_all: false
    indexes :updated_at, type: :date, included_in_all: false
  end


  belongs_to :comment_thread, index: true
  belongs_to :author, class_name: "User", index: true

  attr_accessible :body, :course_id, :anonymous, :anonymous_to_peers, :endorsed, :endorsement

  validates_presence_of :comment_thread, autosave: false
  validates_presence_of :body
  validates_presence_of :course_id
  validates_presence_of :author, autosave: false

  counter_cache :comment_thread

  before_destroy :destroy_children # TODO async

  before_create :set_thread_last_activity_at
  before_update :set_thread_last_activity_at

  def self.hash_tree(nodes)
    nodes.map{|node, sub_nodes| node.to_hash.merge("children" => hash_tree(sub_nodes).compact)}
  end

  # This should really go somewhere else, but sticking it here for now. This is
  # used to flatten out the subtree fetched by calling self.subtree. This is
  # equivalent to calling descendants_and_self; however, calling
  # descendants_and_self and subtree both is very inefficient. It's cheaper to
  # just flatten out the subtree, and simpler than duplicating the code that
  # actually creates the subtree.
  def self.flatten_subtree(x)
    if x.is_a? Array
      x.flatten.map{|y| self.flatten_subtree(y)}
    elsif x.is_a? Hash
      x.to_a.map{|y| self.flatten_subtree(y)}.flatten
    else
      x
    end
  end

  def to_hash(params={})
    sort_by_parent_and_time = Proc.new do |x, y|
      arr_cmp = x.parent_ids.map(&:to_s) <=> y.parent_ids.map(&:to_s)
      if arr_cmp != 0
        arr_cmp
      else
        x.created_at <=> y.created_at
      end
    end
    if params[:recursive]
      # TODO: remove and reuse the new hierarchical sort keys if possible
      subtree_hash = subtree(sort: sort_by_parent_and_time)
      self.class.hash_tree(subtree_hash).first
    else
      as_document.slice(*%w[body course_id endorsed endorsement anonymous anonymous_to_peers created_at updated_at at_position_list])
                 .merge("id" => _id)
                 .merge("user_id" => author_id)
                 .merge("username" => author_username)
                 .merge("depth" => depth)
                 .merge("closed" => comment_thread.nil? ? false : comment_thread.closed) # ditto
                 .merge("thread_id" => comment_thread_id)
                 .merge("commentable_id" => comment_thread.nil? ? nil : comment_thread.commentable_id) # ditto
                 .merge("votes" => votes.slice(*%w[count up_count down_count point]))
                 .merge("abuse_flaggers" => abuse_flaggers)
                 .merge("type" => "comment")
    end
  end

  def commentable_id
    #we need this to have a universal access point for the flag rake task
    if self.comment_thread_id
      t = CommentThread.find self.comment_thread_id
      if t
        t.commentable_id
      end
    end
  rescue Mongoid::Errors::DocumentNotFound
    nil
  end

  def group_id
    if self.comment_thread_id
      t = CommentThread.find self.comment_thread_id
      if t
        t.group_id
      end
    end
  rescue Mongoid::Errors::DocumentNotFound
    nil
  end

  def self.by_date_range_and_thread_ids from_when, to_when, thread_ids
     #return all content between from_when and to_when

     self.where(:created_at.gte => (from_when)).where(:created_at.lte => (to_when)).
       where(:comment_thread_id.in => thread_ids)
  end

  def set_thread_last_activity_at
    self.comment_thread.update_attributes!(last_activity_at: Time.now.utc)
  end


class User(mongoengine.Document):
  include Mongoid::Document
  include Mongo::Voter

  field :_id, type: String, default: -> { external_id }
  field :external_id, type: String
  field :username, type: String
  field :default_sort_key, type: String, default: "date"

  embeds_many :read_states
  has_many :comments, inverse_of: :author
  has_many :comment_threads, inverse_of: :author
  has_many :activities, class_name: "Notification", inverse_of: :actor
  has_and_belongs_to_many :notifications, inverse_of: :receivers

  validates_presence_of :external_id
  validates_presence_of :username
  validates_uniqueness_of :external_id
  validates_uniqueness_of :username

  index( {external_id: 1}, {unique: true, background: true} )

  def subscriptions_as_source
    Subscription.where(source_id: id.to_s, source_type: self.class.to_s)
  end

  def subscribed_thread_ids
    Subscription.where(subscriber_id: id.to_s, source_type: "CommentThread").only(:source_id).map(&:source_id)
  end

  def subscribed_threads
    CommentThread.in({"_id" => subscribed_thread_ids})
  end

  def to_hash(params={})
    hash = as_document.slice(*%w[username external_id])
    if params[:complete]
      hash = hash.merge("subscribed_thread_ids" => subscribed_thread_ids,
                        "subscribed_commentable_ids" => [], # not used by comment client.  To be removed once removed from comment client.
                        "subscribed_user_ids" => [], # ditto.
                        "follower_ids" => [], # ditto.
                        "id" => id,
                        "upvoted_ids" => upvoted_ids,
                        "downvoted_ids" => downvoted_ids,
                        "default_sort_key" => default_sort_key
                       )
    end
    if params[:course_id]
      self.class.trace_execution_scoped(['Custom/User.to_hash/count_comments_and_threads']) do
        if not params[:group_ids].empty?
          # Get threads in either the specified group(s) or posted to all groups (nil).
          specified_groups_or_global = params[:group_ids] << nil
          threads_count = CommentThread.where(
            author_id: id,
            course_id: params[:course_id],
            group_id: {"$in" => specified_groups_or_global},
            anonymous: false,
            anonymous_to_peers: false
          ).count

          # Note that the comments may have been responses to a thread not started by author_id.
          comment_thread_ids = Comment.where(
            author_id: id,
            course_id: params[:course_id],
            anonymous: false,
            anonymous_to_peers: false
          ).collect{|c| c.comment_thread_id}

          # Filter to the unique thread ids visible to the specified group(s).
          group_comment_thread_ids = CommentThread.where(
            id: {"$in" => comment_thread_ids.uniq},
            group_id: {"$in" => specified_groups_or_global},
          ).collect{|d| d.id}

          # Now filter comment_thread_ids so it only includes things in group_comment_thread_ids
          # (keeping duplicates so the count will be correct).
          comments_count = comment_thread_ids.count{
            |comment_thread_id| group_comment_thread_ids.include?(comment_thread_id)
          }

        else
          threads_count = CommentThread.where(
            author_id: id,
            course_id: params[:course_id],
            anonymous: false,
            anonymous_to_peers: false
          ).count
          comments_count = Comment.where(
            author_id: id,
            course_id: params[:course_id],
            anonymous: false,
            anonymous_to_peers: false
          ).count
        end
        hash = hash.merge("threads_count" => threads_count, "comments_count" => comments_count)
      end
    end
    hash
  end

  def upvoted_ids
    Content.up_voted_by(self).map(&:id)
  end

  def downvoted_ids
    Content.down_voted_by(self).map(&:id)
  end

  def followers
    subscriptions_as_source.map(&:subscriber)
  end

  def subscribe(source)
    if source._id == self._id and source.class == self.class
      raise ArgumentError, "Cannot follow oneself"
    else
      Subscription.find_or_create_by(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s)
    end
  end

  def unsubscribe(source)
    subscription = Subscription.where(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s).first
    subscription.destroy if subscription
    subscription
  end

  def mark_as_read(thread)
    read_state = read_states.find_or_create_by(course_id: thread.course_id)
    read_state.last_read_times[thread.id.to_s] = Time.now.utc
    read_state.save
  end

  include ::NewRelic::Agent::MethodTracer
  add_method_tracer :to_hash
  add_method_tracer :subscribed_thread_ids
  add_method_tracer :upvoted_ids
  add_method_tracer :downvoted_ids


class ReadState(mongoengine.EmbeddedDocument):

  include Mongoid::Document
  field :course_id, type: String
  field :last_read_times, type: Hash, default: {}
  embedded_in :user

  validates :course_id, uniqueness: true, presence: true

  def to_hash
    to_json
  end



if __name__=='__main__':

    cx = mongoengine.connect('cs_comments_service_development', host='localhost:27018')
