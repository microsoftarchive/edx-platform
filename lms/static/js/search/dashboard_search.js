RequireJS.require([
    'jquery',
    'backbone',
    'js/search/search_app',
    'js/search/search_router',
    'js/search/views/dashboard/search_form',
    'js/search/collections/search_collection',
    'js/search/views/dashboard/search_results_view'
], function ($, Backbone, SearchApp, SearchRouter, DashSearchForm, SearchCollection, DashSearchResultsView) {

    var app = new SearchApp(
        null,
        SearchRouter,
        DashSearchForm,
        SearchCollection,
        DashSearchResultsView
    );
    Backbone.history.start();

});
