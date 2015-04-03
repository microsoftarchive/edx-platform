RequireJS.require([
    'jquery',
    'backbone',
    'js/search/course/search_app',
    'js/search/base/routers/search_router',
    'js/search/course/views/search_form',
    'js/search/base/collections/search_collection',
    'js/search/course/views/search_results_view'
], function ($, Backbone, SearchApp, SearchRouter, CourseSearchForm, SearchCollection, CourseSearchResultsView) {

    var courseId = $('#courseware-search-results').attr('data-course-id');
    var app = new SearchApp(
        courseId,
        SearchRouter,
        CourseSearchForm,
        SearchCollection,
        CourseSearchResultsView
    );
    Backbone.history.start();

});
