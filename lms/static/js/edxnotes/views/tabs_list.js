;(function (define, undefined) {
'use strict';
define([
    'underscore', 'backbone', 'js/edxnotes/views/tab_item'
], function (_, Backbone, TabItemView) {
    var TabsListView = Backbone.View.extend({
        tagName: 'ul',
        className: 'tabs',

        initialize: function (options) {
            _.bindAll(this);
            this.options = options;
            this.collection.on({
                'add': this.createTab,
                'destroy': function (model, collection) {
                    if (model.isActive()) {
                        collection.at(0).activate();
                    }
                }
            });
        },

        render: function () {
            this.collection.each(this.createTab);
            this.collection.at(0).activate();
            return this;
        },

        createTab: function (model) {
            var tab = new TabItemView({
                model: model
            });
            tab.render().$el.appendTo(this.$el);
            return tab;
        }
    });

    return TabsListView;
});
}).call(this, define || RequireJS.define);
