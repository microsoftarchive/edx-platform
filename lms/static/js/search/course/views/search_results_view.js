;(function (define) {

define([
    'js/search/base/views/search_results_view'
], function (SearchResultsView) {

   'use strict';

    return SearchResultsView.extend({

        el: '#courseware-search-results',
        contentElement: '#course-content',
        resultsTemplateId: '#course_search_results-tpl',
        loadingTemplateId: '#search_loading-tpl',
        errorTemplateId: '#search_error-tpl'

    });

});


})(define || RequireJS.define);
