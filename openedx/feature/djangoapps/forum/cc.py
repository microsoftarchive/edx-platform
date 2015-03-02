"""
Compatibility adapter for django_comment_client, replaces lms.lib.comment_client
"""
from bson import json_util, ObjectId
import datetime
from mongoengine.queryset import Q

from lms.lib.comment_client import *

from .models import ForumUser, ForumContent, ForumThread, ForumComment


def json_encoder(obj):
    res = json_util.default(obj)
    if isinstance(res, dict) and len(res)==1:
        if "$oid" in res:
            return res["$oid"]
        elif "$date" in res:
            return res["$date"]
    return res


class CCMixin(object):

    model_class = None
    _model = None

    #@property
    #def _class_name(self):
    #    return self.model_class._class_name

    def _mapped_key(self, key):
        return key

    def _mapped_kwargs(self, kwargs):
        return kwargs

    def __init__(self, model=None, *args, **kwargs):
        if model is None:
            model = self.model_class(*args, **self._mapped_kwargs(kwargs))
        object.__setattr__(self, '_model', model)

    def __getattr__(self, name):
        return getattr(self._model, name)

    def __setattr__(self, name, value):
        return object.__setattr__(self._model, name, value)

    def __getitem__(self, key):
        try:
            return getattr(self, self._mapped_key(key))
        except AttributeError:
            raise KeyError("Field {0} does not exist".format(key))

    def __setitem__(self, key, value):
        return setattr(self, self._mapped_key(key), value)

    def __contains__(self, key):
        return hasattr(self._model, self._mapped_key(key))

    def get(self, *args):
        try:
            return self[args[0]]
        except KeyError:
            if len(args) > 1:
                return args[1]
            else:
                return None

    @property
    def id(self):
        return str(super(CCMixin, self).id)

    # cc compatibility
    @classmethod
    def find(cls, object_id_str):
        """
        """
        model = cls.model_class.objects.get(pk=ObjectId(object_id_str))
        return cls(model=model)

    def retrieve(self, *args, **kwargs):
        """
        """
        return self.to_dict(*args, **kwargs)


class Thread(CCMixin):

    model_class = ForumThread

    def _mapped_key(self, key):
        mapped_key = key
        if key == 'user_id':
            mapped_key = 'author_id'
        return mapped_key

    def _mapped_kwargs(self, kwargs):
        for k in kwargs:
            mapped_key = self._mapped_key(k)
            if k != mapped_key:
                val = kwargs.pop(k)
                kwargs[mapped_key] = val
        return kwargs

    type = "thread"

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

    # cc compatibility
    @classmethod
    def search(cls, query_params):

        course_id = unicode(query_params['course_id'])
        user_id = query_params.get('user_id')
        group_id = query_params.get('group_id')
        group_ids = query_params.get('group_ids')
        commentable_id = query_params.get('commentable_id')
        commentable_ids = query_params.get('commentable_ids')
        page = query_params.get('page', 1)
        per_page = query_params.get('per_page', 20)
        sort_key = query_params.get('sort_key', 'date')
        sort_order = query_params.get('sort_order', 'desc')
        text = query_params.get('text', '')
        flagged = query_params.get('flagged')
        unread = query_params.get('unread')
        unanswered = query_params.get('unanswered')

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

        thread_cursor = ForumThread.objects(course_id=course_id)
        print 'thread_cursor', thread_cursor
        if commentable_ids is not None:
            commentable_ids = commentable_ids.split(',')
            print 'commentable_ids', commentable_ids
            thread_cursor.filter(commentable_id__in=commentable_ids)
            print 'thread_cursor', thread_cursor

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
            print 'group_ids', group_ids
            thread_cursor.filter(cls._make_group_id_filter(group_ids))
        elif group_id:
            print 'group_id', group_id
            thread_cursor.filter(cls._make_group_id_filter([group_id]))
        print 'thread_cursor', thread_cursor
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
            flagged_comment_thread_ids = [doc.comment_thread_id for doc in ForumComment.objects(course_id=course_id, abuse_flaggers__ne=[], abuse_flaggers__exists=True)]
            flagged_thread_ids = [doc.id for doc in thread_cursor.clone().filter(abuse_flaggers__ne=[], abuse_flaggers__exists=True)]
            thread_cursor.filter(id__in=set(flagged_comment_thread_ids + flagged_thread_ids))
            print 'flagged', flagged
            print 'thread_cursor', thread_cursor

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
            endorsed_comment_thread_ids = [doc.comment_thread_id for doc in ForumComment.objects(course_id=course_id, parent_id__exists=False, endorsed=True)]
            thread_cursor.filter(thread_type="question", id__nin=endorsed_comment_thread_ids)
            print 'unanswered', unanswered
            print 'thread_cursor', thread_cursor

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
        print 'sort_criteria', cls._get_sort_criteria(sort_key, sort_order)
        thread_cursor.order_by(*cls._get_sort_criteria(sort_key, sort_order))
        print thread_cursor
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
            print 'unread', unread
            read_dates = {}
            try:
                read_state = ForumUser.read_states.get(course_id=course_id)
                read_dates = read_state["last_read_times"].to_dict()
            except ForumUser.read_states.DoesNotExist:
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
            print 'not unread'
            #        # let the installed paginator library handle pagination
            #        num_pages = [1, (comment_threads.count / per_page.to_f).ceil].max
            #        page = [1, page].max
            #        threads = comment_threads.page(page).per(per_page).to_a
            #      end
            import math
            num_pages = max([1,  math.ceil(thread_cursor.clone().count() / float(per_page))])
            thread_cursor.skip((page - 1) * per_page).limit(per_page)
        print 'thread_cursor', thread_cursor
        #
        #      if threads.length == 0
        #        collection = []
        #      else
        #        pres_threads = ThreadListPresenter.new(threads, request_user, course_id)
        #        collection = pres_threads.to_hash

        # apply wrapper
        threads = [cls(thread).to_dict() for thread in thread_cursor]
        print 'threads', threads
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
        content = ForumComment.objects(Q(parent_id__in=paged_response_ids) | Q(id__in=paged_response_ids)).order_by("+sk")
        #    {"responses" => merge_response_content(content), "response_count" => response_ids.length}
         #  end
        return {
            "responses": self.merge_response_content(content),
            "response_count": len(response_ids)
        }

    def to_dict(self, user_id=None, recursive=False, response_skip=0, response_limit=None):

        #  def to_hash with_responses=false, resp_skip=0, resp_limit=nil
        #    raise ArgumentError unless resp_skip >= 0
        #    raise ArgumentError unless resp_limit.nil? or resp_limit >= 1
        response_skip = int(response_skip) if response_skip else 0
        response_limit = int(response_limit) if response_limit else 20
        assert response_skip >= 0
        assert response_limit >= 1

        #    h = @thread.to_hash
        hash = self._model.to_mongo()
        hash = {k: hash[k] for k in "thread_type title body course_id anonymous anonymous_to_peers commentable_id created_at updated_at at_position_list closed".split(' ')}
        hash.update({
            "id": self.id,
            "user_id": user_id,
            "username": self._model.author.username,
            "votes": {"up" : [ ], "down" : [ ], "up_count" : 0, "down_count" : 0, "count" : 0, "point" : 0},  # votes.slice(*%w[count up_count down_count point]),
            "abuse_flaggers": self._model.abuse_flaggers,
            "type": "thread",
            "group_id": self._model.group_id,
            "pinned": self._model.pinned or False,
            "comments_count": self._model.comment_count
        })

        #    h["read"] = @is_read
        #    h["unread_comments_count"] = @unread_count
        #    h["endorsed"] = @is_endorsed || false
        hash["read"] = False  # FIXME
        hash["unread_comments_count"] = 0  # FIXME
        hash["endorsed"] = False  # FIXME
        #    if with_responses
        if recursive:
            #      if @thread.thread_type.discussion? && resp_skip == 0 && resp_limit.nil?
            if self._model.thread_type == "discussion" and response_skip == 0 and response_limit is None:
                #        content = Comment.where(comment_thread_id: @thread._id).order_by({"sk" => 1})
                #        h["children"] = merge_response_content(content)
                #        h["resp_total"] = content.to_a.select{|d| d.depth == 0 }.length
                content = ForumComment.objects(comment_thread_id=self.id).order_by("+sk")
                hash["children"] = self.merge_response_content(content)
                hash["resp_total"] = len(filter(lambda item: item.depth == 0, content))
            #      else
            else:
                #        responses = Content.where(comment_thread_id: @thread._id).exists(parent_id: false)
                responses = ForumComment.objects(comment_thread_id=self.id, parent_id__exists=False)
                #        case @thread.thread_type
                #        when "question"
                if self._model.thread_type == "question":
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
                    non_endorsed_response_info = self.get_paged_merged_responses(non_endorsed_responses, response_skip, response_limit)
                    #          h["endorsed_responses"] = endorsed_response_info["responses"]
                    #          h["non_endorsed_responses"] = non_endorsed_response_info["responses"]
                    #          h["non_endorsed_resp_total"] = non_endorsed_response_info["response_count"]
                    hash["endorsed_responses"] = endorsed_response_info["responses"]
                    hash["non_endorsed_responses"] = non_endorsed_response_info["responses"]
                    hash["non_endorsed_resp_total"] = non_endorsed_response_info["response_count"]
                #        when "discussion"
                elif self._model.thread_type == "discussion":
                    #          response_info = get_paged_merged_responses(@thread._id, responses, resp_skip, resp_limit)
                    #          h["children"] = response_info["responses"]
                    #          h["resp_total"] = response_info["response_count"]
                    response_info = self.get_paged_merged_responses(responses, response_skip, response_limit)
                    hash["children"] = response_info["responses"]
                    hash["resp_total"] = response_info["response_count"]
                #        end
            #      end
            #      h["resp_skip"] = resp_skip
            #      h["resp_limit"] = resp_limit
            hash["resp_skip"] = response_skip
            hash["resp_limit"] = response_limit
            #    end
        #    h
        #  end
        return hash


class User(CCMixin):

    model_class = ForumUser

    def __init__(self, *args, **kwargs):
        """
        """
        super(User, self).__init__(*args, **kwargs)
        if 'course_id' in kwargs:
            setattr(self, 'course_id', kwargs['course_id'])

    @classmethod
    def from_django_user(cls, user, course_id=None):
        """
        """
        model, __ = cls.model_class.objects.get_or_create(
            id=str(user.id),
            external_id=str(user.id),
            username=user.username,
        )
        return cls(model=model)

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
                threads = ForumThread.objects(
                    author_id=self.id,
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
                comments = ForumComment.objects(
                    author_id=self.id,
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
                group_visible_threads = ForumThread.objects(
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
                threads = ForumThread.objects(
                    author_id=self.id,
                    course_id=unicode(course_id),
                    anonymous=False,
                    anonymous_to_peers=False,
                )
                threads_count = len(list(threads))
                #  comments_count = Comment.where(
                #    author_id: id,
                #    course_id: params[:course_id],
                #    anonymous: false,
                #    anonymous_to_peers: false
                #  ).count
                comments = ForumComment.objects(
                    author_id=self.id,
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

    def active_threads(self, query_params={}):
        # raise NotImplementedError
        #  page = (params["page"] || DEFAULT_PAGE).to_i
        #  per_page = (params["per_page"] || DEFAULT_PER_PAGE).to_i
        #  per_page = DEFAULT_PER_PAGE if per_page <= 0
        page = int(query_params.get("page", 1))
        per_page = int(query_params.get("per_page", 20))
        per_page = 20 if per_page <= 0 else per_page
        #
        #  active_contents = Content.where(author_id: user_id, anonymous: false, anonymous_to_peers: false, course_id: params["course_id"])
        #                           .order_by(updated_at: :desc)
        #
        active_contents = ForumContent.objects(
            author_id=self.id,
            anonymous=False,
            anonymous_to_peers=False,
            course_id=unicode(self.course_id),
        ).order_by('-updated_at')
        #  # Get threads ordered by most recent activity, taking advantage of the fact
        #  # that active_contents is already sorted that way
        #  active_thread_ids = active_contents.inject([]) do |thread_ids, content|
        #    thread_id = content._type == "Comment" ? content.comment_thread_id : content.id
        #    thread_ids << thread_id if not thread_ids.include?(thread_id)
        #    thread_ids
        #  end
        active_thread_ids = []
        for doc in active_contents:
            if doc._type == "CommentThread":
                thread_id = doc.id
            elif doc._type == "Comment":
                thread_id = doc.comment_thread_id
            if thread_id not in active_thread_ids:
                active_thread_ids.append(thread_id)
        #
        #  threads = CommentThread.in({"_id" => active_thread_ids})
        print 'active_thread_ids:', active_thread_ids
        threads = Thread.objects(id__in=active_thread_ids)
        print threads._query
        print 'active_threads:', len(threads)
        #
        #  group_ids = get_group_ids_from_params(params)
        #  if not group_ids.empty?
        #    threads = get_group_id_criteria(threads, group_ids)
        #  end
        # FIXME!
        pass
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
        thread_dicts = [thread.to_mongo() for thread in threads]
        return thread_dicts, 1, 1


