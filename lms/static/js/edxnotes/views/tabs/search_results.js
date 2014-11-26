;(function (define, undefined) {
'use strict';
define([
    'gettext', 'js/edxnotes/views/tab_view',
    'js/edxnotes/views/subview', 'js/edxnotes/views/search_box'
], function (gettext, TabView, SubView, SearchBoxView) {
    var SearchResultsView = TabView.extend({

        SubViewConstructor: SubView.extend({
            id: 'edx-notes-page-search-results'
        }),

        NoResultsViewConstructor: SubView.extend({
            id: 'edx-notes-page-no-search-results',
            render: function () {
                var message = gettext('No results found for "%(query_string)s".');
                this.$el.html(interpolate(message, {
                    query_string: this.options.searchQuery
                }, true));
                return this;
            }
        }),

        tabInfo: {
            name: gettext('Search Results'),
            class_name: 'tab-search-results',
            is_closable: true
        },

        initialize: function (options) {
            TabView.prototype.initialize.call(this, options);
            this.searchResults = null;
            this.searchBox = new SearchBoxView({
                el: this.$('form.search-box').get(0),
                token: this.options.token,
                user: this.options.user,
                courseId: this.options.courseId,
                debug: this.options.debug,
                search: this.onSearch,
                error: this.onSearchError
            });
        },

        getSubView: function () {
            var collection = this.getCollection();
            if (collection) {
                return new this.SubViewConstructor({collection: collection});
            } else {
                return new this.NoResultsViewConstructor({
                    searchQuery: this.searchResults.searchQuery
                });
            }
        },

        getCollection: function () {
            if (this.searchResults && this.searchResults.collection.length) {
                return this.searchResults.collection;
            }

            return null;
        },

        onClose: function () {
            this.searchResults = null;
        },

        onSearch: function (collection, total, searchQuery) {
            this.hideErrorMessage();

            this.searchResults = {
                collection: collection,
                total: total,
                searchQuery: searchQuery
            };

            // If tab doesn't exist, creates it.
            if (!this.tabModel) {
                this.createTab();
            }

            // If tab is not already active, makes it active
            if (!this.tabModel.isActive()) {
                this.tabModel.activate();
            } else { // Otherwise, just re-render content.
                this.renderContent();
            }

        },

        onSearchError: function (errorMessage) {
            this.showErrorMessage(errorMessage);
        }
    });

    return SearchResultsView;
});
}).call(this, define || RequireJS.define);
