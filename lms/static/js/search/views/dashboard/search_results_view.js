;(function (define) {

define([
    'js/search/views/search_results_view'
], function (SearchResultsView) {

   'use strict';

    return SearchResultsView.extend({
        el: '#dashboard-search-results',
        contentElement: '#my-courses',
        resultsTemplateId: '#dashboard_search_results-tpl',
        loadingTemplateId: '#search_loading-tpl',
        errorTemplateId: '#search_error-tpl',
        events: {
            'click .search-back-to-course': 'backToCourses'
        },

        backToCourses: function () {
            this.clear();
            this.trigger('reset');
        }
    });

});


})(define || RequireJS.define);
