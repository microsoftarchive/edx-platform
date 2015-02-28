import datetime

from bson.objectid import ObjectId
from mongoengine import Document, EmbeddedDocument, Q
from mongoengine.fields import BooleanField, DateTimeField, DictField, EmbeddedDocumentField, IntField, ListField, ReferenceField, StringField


class Content(Document):

    meta = {'allow_inheritance': True, 'collection': 'contents'}
    #include Mongo::Voteable

    visible = BooleanField(default=True)
    abuse_flaggers = ListField(default=[])
    historical_abuse_flaggers = ListField(default=[]) #preserve abuse flaggers after a moderator unflags)
    author_username = StringField(default=None)

    updated_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)

    author_id = StringField()
    @property
    def author(self):
        return User.objects.get(id=self.author_id)

    #before_save :set_username
    #def set_username(self):
    #    # avoid having to look this attribute up later, since it does not change
    #    self.author_username = self.author.username

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

    @classmethod
    def find(cls, object_id_str):
        """
        """
        return cls.objects.get(pk=ObjectId(object_id_str))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        if not self.author_username:
            self.author_username = self.author.username
        return super(Content, self).save(*args, **kwargs)


class Thread(Content):

    #include Mongoid::Timestamps
    #extend Enumerize

    #voteable self, :up => +1, :down => -1

    thread_type = StringField(default="discussion")
    #enumerize :thread_type, in: [:question, :discussion]
    comment_count = IntField(default=0)
    title = StringField()
    body = StringField()
    course_id = StringField()
    commentable_id = StringField()
    anonymous = BooleanField(default=False)
    anonymous_to_peers = BooleanField(default=False)
    closed = BooleanField(default=False)
    at_position_list = ListField(default=[])
    last_activity_at = DateTimeField(default=datetime.datetime.utcnow)
    group_id = IntField()
    pinned = BooleanField(default=False)

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

    @staticmethod
    def merge_response_content(content):
        #  # Takes content output from Mongoid in a depth-first traversal order and
        #  # returns an array of first-level response hashes with content represented
        #  # hierarchically, with a comment's list of children in the key "children".
        #  def merge_response_content(content)
        #    top_level = []
        #    ancestry = []
        #    content.each do |item|
        #      item_hash = item.to_hash.merge("children" => [])
        #      if item.parent_id.nil?
        #        top_level << item_hash
        #        ancestry = [item_hash]
        #      else
        #        while ancestry.length > 0 do
        #          if item.parent_id == ancestry.last["id"]
        #            ancestry.last["children"] << item_hash
        #            ancestry << item_hash
        #            break
        #          else
        #            ancestry.pop
        #            next
        #          end
        #        end
        #        if ancestry.empty? # invalid parent; ignore item
        #          next
        #        end
        #      end
        #    end
        #    top_level
        #  end
        print 'merge response content:', list(content)
        top_level = []
        ancestry = []
        for item in content:
            item_hash = item.to_dict()
            item_hash.update({"children": []})
            if item.parent_id is None:
                top_level.append(item_hash)
                ancestry = [item_hash]
            else:
                while len(ancestry) > 0:
                    if item.parent_id == ancestry[-1:]["id"]:
                        ancestry[-1:]["children"].append(item_hash)
                        ancestry.append(item_hash)
                        break
                    else:
                        ancestry.pop()
                        continue
                if len(ancestry)==0:  # invalid parent; ignore item
                    continue
        print 'merge result:', top_level
        return top_level

    def get_paged_merged_responses(self, responses, skip, limit):
        #  # Given a Mongoid object representing responses, apply pagination and return
        #  # a hash containing the following:
        #  #   responses
        #  #     An array of hashes representing the page of responses (including
        #  #     children)
        #  #   response_count
        #  #     The total number of responses
        #  def get_paged_merged_responses(thread_id, responses, skip, limit)
        #    response_ids = responses.only(:_id).sort({"sk" => 1}).to_a.map{|doc| doc["_id"]}
        response_ids = [doc.id for doc in responses.only("id").order_by("+sk")]
        #    paged_response_ids = limit.nil? ? response_ids.drop(skip) : response_ids.drop(skip).take(limit)
        paged_response_ids = response_ids[skip:] if limit is None else response_ids[skip:limit+1]
        #    content = Comment.where(comment_thread_id: thread_id).
        #      or({:parent_id => {"$in" => paged_response_ids}}, {:id => {"$in" => paged_response_ids}}).
        #      sort({"sk" => 1})
        content = Comment.objects(Q(parent_id__in=paged_response_ids) | Q(id__in=paged_response_ids)).order_by("+sk")
        #    {"responses" => merge_response_content(content), "response_count" => response_ids.length}
         #  end
        return {
            "responses": self.merge_response_content(content),
            "response_count": len(response_ids)
        }

    def to_dict(self, user=None, with_responses=False, resp_skip=0, resp_limit=None):

        assert resp_skip >= 0
        assert resp_limit is None or resp_limit >= 1

        hash = self.to_mongo()
        hash = {k: hash[k] for k in "thread_type title body course_id anonymous anonymous_to_peers commentable_id created_at updated_at at_position_list closed".split(' ')}
        hash.update({
            "id": self.id,
            "user_id": self.author.id,
            "username": self.author.username,
            "votes": {"up" : [ ], "down" : [ ], "up_count" : 0, "down_count" : 0, "count" : 0, "point" : 0},  # votes.slice(*%w[count up_count down_count point]),
            "abuse_flaggers": self.abuse_flaggers,
            "type": "thread",
            "group_id": self.group_id,
            "pinned": self.pinned or False,
            "comments_count": self.comment_count
        })

        #  def to_hash with_responses=false, resp_skip=0, resp_limit=nil
        #    raise ArgumentError unless resp_skip >= 0
        #    raise ArgumentError unless resp_limit.nil? or resp_limit >= 1
        #    h = @thread.to_hash
        #    h["read"] = @is_read
        #    h["unread_comments_count"] = @unread_count
        #    h["endorsed"] = @is_endorsed || false
        hash["read"] = False  # FIXME
        hash["unread_comments_count"] = 0  # FIXME
        hash["endorsed"] = False  # FIXME
        #    if with_responses
        if with_responses:
            #      if @thread.thread_type.discussion? && resp_skip == 0 && resp_limit.nil?
            if self.thread_type == "discussion" and resp_skip == 0 and resp_limit is None:
                #        content = Comment.where(comment_thread_id: @thread._id).order_by({"sk" => 1})
                #        h["children"] = merge_response_content(content)
                #        h["resp_total"] = content.to_a.select{|d| d.depth == 0 }.length
                content = Comment.objects(comment_thread_id=self.id).order_by("+sk")
                hash["children"] = self.merge_response_content(content)
                hash["resp_total"] = len(filter(lambda item: item.depth == 0, content))
                print 'discussion responses default', hash
            #      else
            else:
                #        responses = Content.where(comment_thread_id: @thread._id).exists(parent_id: false)
                responses = Comment.objects(comment_thread_id=self.id, parent_id__exists=False)
                #        case @thread.thread_type
                #        when "question"
                if self.thread_type == "question":
                    #          endorsed_responses = responses.where(endorsed: true)
                    #          non_endorsed_responses = responses.where(endorsed: false)
                    endorsed_responses = responses.clone().filter(endorsed=True)
                    non_endorsed_responses = responses.clone().filter(endorsed=False)
                    #          endorsed_response_info = get_paged_merged_responses(@thread._id, endorsed_responses, 0, nil)
                    #          non_endorsed_response_info = get_paged_merged_responses(
                    #            @thread._id,
                    #            non_endorsed_responses,
                    #            resp_skip,
                    #            resp_limit
                    #          )
                    endorsed_response_info = self.get_paged_merged_responses(endorsed_responses, 0, None)
                    non_endorsed_response_info = self.get_paged_merged_responses(non_endorsed_responses, resp_skip, resp_limit)
                    #          h["endorsed_responses"] = endorsed_response_info["responses"]
                    #          h["non_endorsed_responses"] = non_endorsed_response_info["responses"]
                    #          h["non_endorsed_resp_total"] = non_endorsed_response_info["response_count"]
                    hash["endorsed_responses"] = endorsed_response_info["responses"]
                    hash["non_endorsed_responses"] = non_endorsed_response_info["responses"]
                    hash["non_endorsed_resp_total"] = non_endorsed_response_info["response_count"]
                    print 'question responses', hash
                #        when "discussion"
                elif self.thread_type == "discussion":
                    #          response_info = get_paged_merged_responses(@thread._id, responses, resp_skip, resp_limit)
                    #          h["children"] = response_info["responses"]
                    #          h["resp_total"] = response_info["response_count"]
                    response_info = self.get_paged_merged_responses(responses, resp_skip, resp_limit)
                    hash["children"] = response_info["responses"]
                    hash["resp_total"] = response_info["response_count"]
                    print 'discussion responses', hash
                #        end
            #      end
            #      h["resp_skip"] = resp_skip
            #      h["resp_limit"] = resp_limit
            hash["resp_skip"] = resp_skip
            hash["resp_limit"] = resp_limit
            #    end
        #    h
        #  end
        return hash
#

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

    #  def get_sort_criteria(sort_key, sort_order)
    #    sort_key_mapper = {
    #      "date" => :created_at,
    #      "activity" => :last_activity_at,
    #      "votes" => :"votes.point",
    #      "comments" => :comment_count,
    #    }
    #
    #    sort_order_mapper = {
    #      "desc" => :desc,
    #      "asc" => :asc,
    #    }
    #
    #    sort_key = sort_key_mapper[params["sort_key"] || "date"]
    #    sort_order = sort_order_mapper[params["sort_order"] || "desc"]
    #
    #    if sort_key && sort_order
    #      sort_criteria = [[:pinned, :desc], [sort_key, sort_order]]
    #      if ![:created_at, :last_activity_at].include? sort_key
    #        sort_criteria << [:created_at, :desc]
    #      end
    #      sort_criteria
    #    else
    #      nil
    #    end
    #  end
    @staticmethod
    def _get_sort_criteria(sort_key, sort_order):
        """
        """
        sort_key = {
            "date": "created_at",
            "activity": "last_activity_at",
            "votes": "votes.point",
            "comments": "comment_count",
        }.get(sort_key, "created_at")

        sort_order = {
            "desc": "-",
            "asc": "+",
        }.get(sort_order, "-")

        sort_criteria = ["-pinned", sort_order + sort_key]
        if not sort_key.endswith("_at"):
            sort_criteria.append("-created_at")

        return sort_criteria

    #  def get_group_id_criteria(threads, group_ids)
    #    if group_ids.length > 1
    #      threads.any_of(
    #        {"group_id" => {"$in" => group_ids}},
    #        {"group_id" => {"$exists" => false}},
    #      )
    #    else
    #      threads.any_of(
    #        {"group_id" => group_ids[0]},
    #        {"group_id" => {"$exists" => false}},
    #      )
    #    end
    #  end
    @staticmethod
    def _make_group_id_filter(group_ids):
        """
        """
        if len(group_ids) > 1:
            return Q(Q(group_id__in=group_ids)|Q(group_id__exists=False))
        else:
            return Q(Q(group_id=group_ids[0])|Q(group_id__exists=False))


    @classmethod
    def search(
        cls,
        user,
        course_id,
        group_id=None,
        group_ids=None,
        commentable_id=None,
        commentable_ids=None,
        page=1,
        per_page=20,
        sort_key='date',
        sort_order='desc',
        text='',
        flagged=None,
        unread=None,
        unanswered=None,
    ):

        #default_params = {'page': 1,
        #                  'per_page': 20,
        #                  'course_id': query_params['course_id'],
        #                  'recursive': False}
        #params = merge_dict(default_params, strip_blank(strip_none(query_params)))
        #
        #if query_params.get('text'):
        #    url = cls.url(action='search')
        #else:
        #    url = cls.url(action='get_all', params=extract(params, 'commentable_id'))
        #    if params.get('commentable_id'):
        #        del params['commentable_id']
        #response = perform_request(
        #    'get',
        #    url,
        #    params,
        #    metric_tags=[u'course_id:{}'.format(query_params['course_id'])],
        #    metric_action='thread.search',
        #    paged_results=True
        #)

        thread_cursor = Thread.objects(course_id=course_id)
        if commentable_ids is not None:
            thread_cursor.filter(commentable_id__in=commentable_ids)

        #  def handle_threads_query(
        #    comment_threads,
        #    user_id,
        #    course_id,
        #    group_ids,
        #    filter_flagged,
        #    filter_unread,
        #    filter_unanswered,
        #    sort_key,
        #    sort_order,
        #    page,
        #    per_page
        #  )
        #
        #    if not group_ids.empty?
        #      comment_threads = get_group_id_criteria(comment_threads, group_ids)
        #    end
        if group_ids:
            thread_cursor.filter(cls._make_group_id_filter(group_ids))
        elif group_id:
            thread_cursor.filter(cls._make_group_id_filter([group_id]))
        #
        #    if filter_flagged
        if flagged:
            #      self.class.trace_execution_scoped(['Custom/handle_threads_query/find_flagged']) do
            #        # TODO replace with aggregate query?
            #        comment_ids = Comment.where(:course_id => course_id).
            #          where(:abuse_flaggers.ne => [], :abuse_flaggers.exists => true).
            #          collect{|c| c.comment_thread_id}.uniq
            #
            #        thread_ids = comment_threads.where(:abuse_flaggers.ne => [], :abuse_flaggers.exists => true).
            #          collect{|c| c.id}
            #
            #        comment_threads = comment_threads.in({"_id" => (comment_ids + thread_ids).uniq})
            #      end
            #    end
            #
            flagged_comment_thread_ids = [doc.comment_thread_id for doc in Comment.objects(course_id=course_id, abuse_flaggers__ne=[], abuse_flaggers__exists=True)]
            flagged_thread_ids = [doc.id for doc in thread_cursor.clone().filter(abuse_flaggers__ne=[], abuse_flaggers__exists=True)]
            thread_cursor.filter(id__in=set(flagged_comment_thread_ids + flagged_thread_ids))

        #    if filter_unanswered
        if unanswered:
            #      self.class.trace_execution_scoped(['Custom/handle_threads_query/find_unanswered']) do
            #        endorsed_thread_ids = Comment.where(:course_id => course_id).
            #          where(:parent_id.exists => false, :endorsed => true).
            #          collect{|c| c.comment_thread_id}.uniq
            #
            #        comment_threads = comment_threads.where({"thread_type" => :question}).nin({"_id" => endorsed_thread_ids})
            #      end
            #    end
            endorsed_comment_thread_ids = [doc.comment_thread_id for doc in Comment.objects(course_id=course_id, parent_id__exists=False, endorsed=True)]
            thread_cursor.filter(thread_type="question", id__nin=endorsed_comment_thread_ids)
        #
        #    sort_criteria = get_sort_criteria(sort_key, sort_order)
        #    if not sort_criteria
        #      {}
        #    else
        #      request_user = user_id ? user : nil
        #      page = (page || DEFAULT_PAGE).to_i
        #      per_page = (per_page || DEFAULT_PER_PAGE).to_i
        #
        #      comment_threads = comment_threads.order_by(sort_criteria)
        #
        thread_cursor.order_by(*cls._get_sort_criteria(sort_key, sort_order))
        #      if request_user and filter_unread
        #        # Filter and paginate based on user read state.  Requires joining a subdocument of the
        #        # user object with documents in the contents collection, which has to be done in memory.
        #        read_dates = {}
        #        read_state = request_user.read_states.where(:course_id => course_id).first
        #        if read_state
        #          read_dates = read_state["last_read_times"].to_hash
        #        end
        #
        if unread:
            read_dates = {}
            try:
                read_state = User.read_states.get(course_id=course_id)
                read_dates = read_state["last_read_times"].to_dict()
            except User.read_states.DoesNotExist:
                pass

            #        threads = []
            #        skipped = 0
            #        to_skip = (page - 1) * per_page
            #        has_more = false
            #        # batch_size is used to cap the number of documents we might load into memory at any given time
            #        # TODO: starting with Mongoid 3.1, you can just do comment_threads.batch_size(size).each()
            #        comment_threads.query.batch_size(CommentService.config["manual_pagination_batch_size"].to_i)
            #        Mongoid.unit_of_work(disable: :current) do # this is to prevent Mongoid from memoizing every document we look at
            #          comment_threads.each do |thread|
            threads = []
            skipped = 0
            to_skip = (page - 1) * per_page
            has_more = False
            for doc in thread_cursor:
                #            thread_key = thread._id.to_s
                #            if !read_dates.has_key?(thread_key) || read_dates[thread_key] < thread.last_activity_at
                #              if skipped >= to_skip
                #                if threads.length == per_page
                #                  has_more = true
                #                  break
                #                end
                #                threads << thread
                #              else
                #                skipped += 1
                #              end
                #            end
                #          end
                #        end
                #        # The following trick makes frontend pagers work without recalculating
                #        # the number of all unread threads per user on every request (since the number
                #        # of threads in a course could be tens or hundreds of thousands).  It has the
                #        # effect of showing that there's always just one more page of results, until
                #        # there definitely are no more pages.  This is really only acceptable for pagers
                #        # that don't actually reveal the total number of pages to the user onscreen.
                #        num_pages = has_more ? page + 1 : page
                thread_key = str(doc.id)
                if thread_key not in read_dates or read_dates[thread_key] < doc.last_activity_at:
                    if skipped >= to_skip:
                        if len(threads) == per_page:
                            has_more = True
                            break
                        threads.append(doc)
                    else:
                        skipped += 1
            num_pages = page + 1 if has_more else page
        #      else
        else:
            #        # let the installed paginator library handle pagination
            #        num_pages = [1, (comment_threads.count / per_page.to_f).ceil].max
            #        page = [1, page].max
            #        threads = comment_threads.page(page).per(per_page).to_a
            #      end
            import math
            num_pages = max([1,  math.ceil(thread_cursor.clone().count() / float(per_page))])
            thread_cursor.skip((page - 1) * per_page).limit(per_page)
        #
        #      if threads.length == 0
        #        collection = []
        #      else
        #        pres_threads = ThreadListPresenter.new(threads, request_user, course_id)
        #        collection = pres_threads.to_hash
        threads = [thread.to_dict() for thread in thread_cursor]
        #      end
        #      {collection: collection, num_pages: num_pages, page: page}
        meta = {num_pages: num_pages, page: page}



        #if query_params.get('text'):
        #    search_query = query_params['text']
        #    course_id = query_params['course_id']
        #    group_id = query_params['group_id'] if 'group_id' in query_params else None
        #    requested_page = params['page']
        #    total_results = response.get('total_results')
        #    corrected_text = response.get('corrected_text')
        #    # Record search result metric to allow search quality analysis.
        #    # course_id is already included in the context for the event tracker
        #    tracker.emit(
        #        'edx.forum.searched',
        #        {
        #            'query': search_query,
        #            'corrected_text': corrected_text,
        #            'group_id': group_id,
        #            'page': requested_page,
        #            'total_results': total_results,
        #        }
        #    )
        #    log.info(
        #        u'forum_text_search query="{search_query}" corrected_text="{corrected_text}" course_id={course_id} group_id={group_id} page={requested_page} total_results={total_results}'.format(
        #            search_query=search_query,
        #            corrected_text=corrected_text,
        #            course_id=course_id,
        #            group_id=group_id,
        #            requested_page=requested_page,
        #            total_results=total_results
        #        )
        #    )
        return threads, meta.get('page', 1), meta.get('num_pages', 1), meta.get('corrected_text')



class Comment(Content):

    #include Mongoid::Tree
    #include Mongoid::Timestamps
    #include Mongoid::MagicCounterCache

    #voteable self, :up => +1, :down => -1

    course_id = StringField()
    body = StringField()
    endorsed = BooleanField(default=False)
    endorsement = DictField()
    anonymous = BooleanField(default=False)
    anonymous_to_peers = BooleanField(default=False)
    at_position_list = ListField(default=[])

    parent_id = ReferenceField('Comment')
    parent_ids = ListField(ReferenceField('Comment'))

    #index({author_id: 1, course_id: 1})
    #index({_type: 1, comment_thread_id: 1, author_id: 1, updated_at: 1})

    sk = StringField(default=None)
    #before_save :set_sk
    #def set_sk(self):
    #    # this attribute is explicitly write-once
    #    if self.sk is None:

    def save(self, *args, **kwargs):
        if not self.sk:
            self.sk = "-".join([str(oid) for oid in (self.parent_ids + [self.id])])
        return super(Comment, self).save(*args, **kwargs)


    comment_thread_id = ReferenceField('Thread', dbref=False)
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
        return Thread.objects.get(id=self.comment_thread_id)

    @property
    def commentable_id(self):
        raise NotImplementedError
        ##we need this to have a universal access point for the flag rake task
        #if self.comment_thread_id
        #t = CommentThread.find self.comment_thread_id
        #if t
        #t.commentable_id
        #
        #rescue Mongoid::Errors::DocumentNotFound
        #None

    @property
    def group_id(self):
        raise NotImplementedError
        #if self.comment_thread_id
        #t = CommentThread.find self.comment_thread_id
        #if t
        #t.group_id
        #
        #rescue Mongoid::Errors::DocumentNotFound
        #None

    @classmethod
    def by_date_range_and_thread_ids(cls, from_when, to_when, thread_ids):
        raise NotImplementedError
        #return all content between from_when and to_when
        #self.where(:created_at.gte => (from_when)).where(:created_at.lte => (to_when)).
        #where(:comment_thread_id.in => thread_ids)


    def set_thread_last_activity_at(self):
        raise NotImplementedError
        #self.comment_thread.update_attributes!(last_activity_at: Time.now.utc)



class User(Document):

    meta = {'collection': 'users'}
    #include Mongo::Voter

    id = StringField(primary_key=True)
    external_id = StringField()
    # the above two need to be kept in sync
    username = StringField()
    default_sort_key = StringField(default="date")

    comments = ListField(ReferenceField('Comment'))
    threads = ListField(ReferenceField('Thread'))
    read_states = ListField(EmbeddedDocumentField('ReadState'))
    #has_many :comments, inverse_of: :author
    #has_many :comment_threads, inverse_of: :author
    #has_many :activities, class_name: "Notification", inverse_of: :actor
    #has_and_belongs_to_many :notifications, inverse_of: :receivers

    #validates_presence_of :external_id
    #validates_presence_of :username
    #validates_uniqueness_of :external_id
    #validates_uniqueness_of :username

    #index( {external_id: 1}, {unique: true, background: true} )

    @classmethod
    def from_django_user(cls, user, course_id=None):
        """
        """
        obj, __ = cls.objects.get_or_create(
            id=str(user.id),
            external_id=str(user.id),
            username=user.username,
        )
        if course_id:  # get rid of this, not saved to db.
            setattr(obj, 'course_id', course_id)
        return obj

    def follow(self, thread):
        """
        """
        #if source._id == self._id and source.class == self.class
        #  raise ArgumentError, "Cannot follow oneself"
        #else
        #  Subscription.find_or_create_by(subscriber_id: self._id.to_s, source_id: source._id.to_s, source_type: source.class.to_s)
        #end
        #assert isinstance(thread, Thread)
        Subscription.objects.get_or_create(
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
        Subscription.objects(
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
        subs = Subscription.objects(
            subscriber_id=self.id,
            source_type="Thread"
        )
        return [doc.source_id for doc in subs]

    @property
    def subscribed_threads(self):
        raise NotImplementedError
        #CommentThread.in({"_id" => subscribed_thread_ids})


    def to_dict(self, params={}):
        course_id = params.get('course_id', getattr(self, 'course_id', None))
        #hash = as_document.slice(*%w[username external_id])
        hash = {
            "username": self.username,
            "external_id": self.external_id
        }
        #if params[:complete]
        if params.get('complete', True):
            #hash = hash.merge("subscribed_thread_ids" => subscribed_thread_ids,
            #                "subscribed_commentable_ids" => [], # not used by comment client.  To be removed once removed from comment client.
            #                "subscribed_user_ids" => [], # ditto.
            #                "follower_ids" => [], # ditto.
            #                "id" => id,
            #                "upvoted_ids" => upvoted_ids,
            #                "downvoted_ids" => downvoted_ids,
            #                "default_sort_key" => default_sort_key
            #               )
            hash.update({
                "subscribed_thread_ids": self.subscribed_thread_ids,
                "id": self.id,
                "upvoted_ids": self.upvoted_ids,
                "downvoted_ids": self.downvoted_ids,
                "default_sort_key": self.default_sort_key,
            })
        #
        #if params[:course_id]
        if course_id:
            #self.class.trace_execution_scoped(['Custom/User.to_hash/count_comments_and_threads']) do
            #if not params[:group_ids].empty?
            if params.get('group_ids'):
                #  # Get threads in either the specified group(s) or posted to all groups (None).
                #  specified_groups_or_global = params[:group_ids] << None
                #  threads_count = CommentThread.where(
                #    author_id: id,
                #    course_id: params[:course_id],
                #    group_id: {"$in" => specified_groups_or_global},
                #    anonymous: false,
                #    anonymous_to_peers: false
                #  ).count
                threads = Thread.objects(
                    author=self,
                    course_id=unicode(course_id),
                    group_id__in=params['group_ids'] + [None],
                    anonymous=False,
                    anonymous_to_peers=False,
                )
                threads_count = len(list(threads))

                #
                #  # Note that the comments may have been responses to a thread not started by author_id.
                #  comment_thread_ids = Comment.where(
                #    author_id: id,
                #    course_id: params[:course_id],
                #    anonymous: false,
                #    anonymous_to_peers: false
                #  ).collect{|c| c.comment_thread_id}
                comments = Comment.objects(
                    author=self,
                    course_id=unicode(course_id),
                    anonymous=False,
                    anonymous_to_peers=False,
                )
                comment_thread_ids = set(list(doc.comment_thread_id for doc in comments))

                #  # Filter to the unique thread ids visible to the specified group(s).
                #  group_comment_thread_ids = CommentThread.where(
                #    id: {"$in" => comment_thread_ids.uniq},
                #    group_id: {"$in" => specified_groups_or_global},
                #  ).collect{|d| d.id}
                group_visible_threads = Thread.objects(
                    id__in=comment_thread_ids,
                    group_id__in=params['group_ids'] + [None]
                )
                group_visible_thread_ids = set(list(doc.id for doc in group_visible_threads))
                #
                #  # Now filter comment_thread_ids so it only includes things in group_comment_thread_ids
                #  # (keeping duplicates so the count will be correct).
                #  comments_count = comment_thread_ids.count{
                #    |comment_thread_id| group_comment_thread_ids.include?(comment_thread_id)
                #  }
                #
                comments_count = 0
                for comment_thread_id in comment_thread_ids:
                    if comment_thread_id in group_visible_thread_ids:
                        comments_count += 1

            else:
                #  threads_count = CommentThread.where(
                #    author_id: id,
                #    course_id: params[:course_id],
                #    anonymous: false,
                #    anonymous_to_peers: false
                #  ).count
                threads = Thread.objects(
                    author=self,
                    course_id=unicode(course_id),
                    anonymous=False,
                    anonymous_to_peers=False,
                )
                print 'threads', list(threads)
                threads_count = len(list(threads))
                #  comments_count = Comment.where(
                #    author_id: id,
                #    course_id: params[:course_id],
                #    anonymous: false,
                #    anonymous_to_peers: false
                #  ).count
                comments = Comment.objects(
                    author=self,
                    course_id=unicode(course_id),
                    anonymous=False,
                    anonymous_to_peers=False,
                )
                comments_count = len(list(comments))
            #
            #hash = hash.merge("threads_count" => threads_count, "comments_count" => comments_count)
            hash.update({
                "threads_count": threads_count,
                "comments_count": comments_count,
            })
            #
        #hash
        return hash

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

    def active_threads(self, query_params={}):
        # raise NotImplementedError
        #  page = (params["page"] || DEFAULT_PAGE).to_i
        #  per_page = (params["per_page"] || DEFAULT_PER_PAGE).to_i
        #  per_page = DEFAULT_PER_PAGE if per_page <= 0
        #
        #  active_contents = Content.where(author_id: user_id, anonymous: false, anonymous_to_peers: false, course_id: params["course_id"])
        #                           .order_by(updated_at: :desc)
        #
        #  # Get threads ordered by most recent activity, taking advantage of the fact
        #  # that active_contents is already sorted that way
        #  active_thread_ids = active_contents.inject([]) do |thread_ids, content|
        #    thread_id = content._type == "Comment" ? content.comment_thread_id : content.id
        #    thread_ids << thread_id if not thread_ids.include?(thread_id)
        #    thread_ids
        #  end
        #
        #  threads = CommentThread.in({"_id" => active_thread_ids})
        #
        #  group_ids = get_group_ids_from_params(params)
        #  if not group_ids.empty?
        #    threads = get_group_id_criteria(threads, group_ids)
        #  end
        #
        #  num_pages = [1, (threads.count / per_page.to_f).ceil].max
        #  page = [num_pages, [1, page].max].min
        #
        #  sorted_threads = threads.sort_by {|t| active_thread_ids.index(t.id)}
        #  paged_threads = sorted_threads[(page - 1) * per_page, per_page]
        #
        #  presenter = ThreadListPresenter.new(paged_threads, user, params[:course_id])
        #  collection = presenter.to_hash
        #
        #  json_output = nil
        #  self.class.trace_execution_scoped(['Custom/get_user_active_threads/json_serialize']) do
        #    json_output = {
        #      collection: collection,
        #      num_pages: num_pages,
        #      page: page,
        #    }.to_json
        #  end
        #  json_output
        #
        #
        #
        #
        # url = _url_for_user_active_threads(self.id)
        # params = {'course_id': self.course_id.to_deprecated_string()}
        # params = merge_dict(params, query_params)
        # response = perform_request(
        #     'get',
        #     url,
        #     params,
        #     metric_action='user.active_threads',
        #     metric_tags=self._metric_tags,
        #     paged_results=True,
        # )
        # return response.get('collection', []), response.get('page', 1), response.get('num_pages', 1)
        return [], 1, 1




class ReadState(EmbeddedDocument):

    course_id = StringField()
    last_read_times = DictField(default={})
    #embedded_in :user

    #validates :course_id, uniqueness: true, presence: true

    def to_dict(self):
        return self.to_mongo().to_dict()


class Subscription(Document):
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
        return User.objects.get(self.subscriber_id)

    @property
    def source(self):
        return {
            "Thread": Thread,
            "Comment": Comment,
        }[self.source_type].get(self.source_id)


if __name__=='__main__':

    # host OS
    from mongoengine import connect
    cx = connect('cs_comments_service_development', host='localhost:27018')

else:

    # devstack
    from mongoengine import connect
    cx = connect('cs_comments_service_development')
