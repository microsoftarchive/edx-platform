;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'logger'
    ], function (gettext, $, _, Backbone, Logger) {

        var AccountSettingsView = Backbone.View.extend({

            initialize: function (options) {
                this.template = _.template($('#account_settings-tpl').text());
                this.accountUserId = options.accountUserId;
                _.bindAll(this, 'render', 'renderFields', 'showLoadingError');
            },

            render: function () {
                this.$el.html(this.template({
                    sections: this.options.sectionsData
                }));

                // Record that the account settings page was viewed.
                Logger.log('edx.user.settings.viewed', {
                    user_id: this.accountUserId,
                    page: "account",
                    visibility: null,
                    requires_parental_consent: this.model.get('requires_parental_consent')
                });

                return this;
            },

            renderFields: function () {
                this.$('.ui-loading-indicator').addClass('is-hidden');

                var view = this;
                _.each(this.$('.account-settings-section-body'), function (sectionEl, index) {
                    _.each(view.options.sectionsData[index].fields, function (field) {
                        $(sectionEl).append(field.view.render().el);
                    });
                });
                return this;
            },

            showLoadingError: function () {
                this.$('.ui-loading-indicator').addClass('is-hidden');
                this.$('.ui-loading-error').removeClass('is-hidden');
            }
        });

        return AccountSettingsView;
    });
}).call(this, define || RequireJS.define);
