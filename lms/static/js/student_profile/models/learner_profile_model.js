;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'underscore', 'backbone'
    ], function (gettext, _, Backbone) {

        var LearnerProfileModel = Backbone.Model.extend({
            defaults: {
                username: '',
                language: null,
                country: null,
                profile_privacy: "all_users",
                bio: ''
            }
        });

        return LearnerProfileModel;
    })
}).call(this, define || RequireJS.define);