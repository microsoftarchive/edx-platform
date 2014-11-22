;(function (define, undefined) {
'use strict';
define([
    'underscore', 'backbone', 'js/edxnotes/models/tab'
], function (_, Backbone, TabModel) {
    var TabView = Backbone.View.extend({

        SubViewConstructor: null,

        tabInfo: {
            name: '',
            class_name: ''
        },

        initialize: function (options) {
            _.bindAll(this);
            this.options = _.defaults(options, {
                createTabOnInitialization: true
            });

            if (this.options.createTabOnInitialization) {
                this.createTab();
            }
        },

        /**
         * Creates a tab for the view.
         */
        createTab: function () {
            this.tabModel = new TabModel(this.tabInfo);
            this.options.tabsCollection.add(this.tabModel);

            this.tabModel.on({
                'change:is_active': _.bind(function (model, value) {
                    if (value) {
                        this.renderContent();
                    } else if (this.contentView) {
                        this.contentView.destroy();
                        this.contentView = null;
                    }
                }, this),
                'destroy': _.bind(function () {
                    if (this.contentView) {
                        this.contentView.destroy();
                    }
                    this.contentView = null;
                    this.tabModel = null;
                    this.onClose();
                }, this)
            });
        },

        /**
         * Renders content for the view.
         */
        renderContent: function () {
            this.showLoadingIndicator();
            // If the view is already rendered, destroy it.
            if (this.contentView) {
                this.contentView.destroy();
            }

            this.contentView = this.getSubView();
            this.$('.course-info').append(this.contentView.render().$el);
            this.hideLoadingIndicator();

            return this;
        },

        getSubView: function () {
            var collection = this.getCollection();
            return new this.SubViewConstructor({collection: collection});
        },

        /**
         * Returns collection for the view.
         * @return {Backbone.Collection}
         */
        getCollection: function () {
            return this.collection;
        },

        /**
         * Callback that is called on closing the tab.
         */
        onClose: function () { },

        /**
         * Shows the page's loading indicator.
         */
        showLoadingIndicator: function() {
            this.$('.ui-loading').removeClass('is-hidden');
        },

        /**
         * Hides the page's loading indicator.
         */
        hideLoadingIndicator: function() {
            this.$('.ui-loading').addClass('is-hidden');
        },


        /**
         * Shows error message.
         */
        showErrorMessage: function (message) {
            this.$('.inline-error')
                .html(message)
                .removeClass('is-hidden');
        },

        /**
         * Hides error message.
         */
        hideErrorMessage: function () {
            this.$('.inline-error')
                .html('')
                .addClass('is-hidden');
        }
    });

    return TabView;
});
}).call(this, define || RequireJS.define);
