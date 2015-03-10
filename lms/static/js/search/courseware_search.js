RequireJS.require([
    'jquery',
    'backbone',
    'js/search/search_app',
    'js/search/search_router',
    'js/search/views/course/search_form',
    'js/search/collections/search_collection',
    'js/search/views/course/search_results_view'
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
