;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone'
    ], function (gettext, $, _, Backbone) {

        var LearnerProfileView = Backbone.View.extend({

            events: {
                'change .profile-visibility>span>select': 'setProfileVisibility'
            },

            initialize: function (options) {
                this.template = _.template($('#learner_profile-tpl').text());
                this.profileData = options.profileData;
            },

            render: function () {
                this.$el.html(this.template({
                    profileData: this.profileData

                }));
                this.$("").append(this.options.profilePhotoView.el);
                return this;
            },

            setProfileVisibility: function (event) {
                this.profileData.profile_visibility = this.getSelectedVisibilityValue();
                // TODO! Send profile visibility selection to server for persistance
                this.render();
            },

            getSelectedVisibilityValue: function () {
                var value = this.$('.profile-visibility > span > select').val();
                return value == 'fp';
            }
        });

        return LearnerProfileView;
    })
}).call(this, define || RequireJS.define);