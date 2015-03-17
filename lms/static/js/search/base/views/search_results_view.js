;(function (define) {

define([
    'jquery',
    'underscore',
    'backbone',
    'gettext',
    'js/search/base/views/search_item_view'
], function ($, _, Backbone, gettext, SearchItemView) {

   'use strict';

    return Backbone.View.extend({

        // to be overridden by subclasses
        el: '',
        contentElement: '',
        resultsTemplateId: '',
        loadingTemplateId: '',
        errorTemplateId: '',

        events: {
            'click .search-load-next': 'loadNext'
        },
        spinner: '.icon',

        initialize: function () {
            this.courseName = this.$el.attr('data-course-name');
            this.$contentElement = $(this.contentElement);
            this.resultsTemplate = _.template($(this.resultsTemplateId).html());
            this.loadingTemplate = _.template($(this.loadingTemplateId).html());
            this.errorTemplate = _.template($(this.errorTemplateId).html());
            this.collection.on('search', this.render, this);
            this.collection.on('next', this.renderNext, this);
            this.collection.on('error', this.showErrorMessage, this);
        },

        render: function () {
            this.$el.html(this.resultsTemplate({
                totalCount: this.collection.totalCount,
                totalCountMsg: this.totalCountMsg(),
                pageSize: this.collection.pageSize,
                hasMoreResults: this.collection.hasNextPage()
            }));
            this.renderItems();
            this.$el.find(this.spinner).hide();
            this.$contentElement.hide();
            this.$el.show();
            return this;
        },

        renderNext: function () {
            // total count may have changed
            this.$el.find('.search-count').text(this.totalCountMsg());
            this.renderItems();
            if (! this.collection.hasNextPage()) {
                this.$el.find('.search-load-next').remove();
            }
            this.$el.find(this.spinner).hide();
        },

        renderItems: function () {
            var items = this.collection.map(function (result) {
                var item = new SearchItemView({ model: result });
                return item.render().el;
            });
            this.$el.find('ol').append(items);
        },

        totalCountMsg: function () {
            var fmt = ngettext('%s result', '%s results', this.collection.totalCount);
            return interpolate(fmt, [this.collection.totalCount]);
        },

        clear: function () {
            this.$el.hide().empty();
            this.$contentElement.show();
        },

        showLoadingMessage: function () {
            this.$el.html(this.loadingTemplate());
            this.$el.show();
            this.$contentElement.hide();
        },

        showErrorMessage: function () {
            this.$el.html(this.errorTemplate());
            this.$el.show();
            this.$contentElement.hide();
        },

        loadNext: function (event) {
            event && event.preventDefault();
            this.$el.find(this.spinner).show();
            this.trigger('next');
        }

    });

});


})(define || RequireJS.define);
