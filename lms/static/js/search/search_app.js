;(function (define) {

define(function() {
    'use strict';

    return function (courseId, SearchRouter, SearchForm, SearchCollection, SearchListView) {

        var self = this;

        this.router = new SearchRouter();
        this.form = new SearchForm();
        this.collection = new SearchCollection([], { courseId: courseId });
        this.results = new SearchListView({ collection: this.collection });

        this.form.on('search', this.results.showLoadingMessage, this.results);
        this.form.on('search', this.collection.performSearch, this.collection);
        this.form.on('search', function (term) {
            self.router.navigate('search/' + term, { replace: true });
        });
        this.form.on('clear', this.collection.cancelSearch, this.collection);
        this.form.on('clear', this.results.clear, this.results);
        this.form.on('clear', this.router.navigate, this.router);

        this.results.on('reset', this.form.resetSearchForm, this.form);
        this.results.on('next', this.collection.loadNextPage, this.collection);
        this.router.on('route:search', this.form.doSearch, this.form);

    };

});

})(define || RequireJS.define);
