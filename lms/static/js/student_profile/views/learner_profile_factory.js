;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone',
        'js/student_profile/models/learner_profile_model',
        'js/student_profile/views/learner_profile_view'
    ], function (gettext, $, _, Backbone, LearnerProfileModel, LearnerProfileView) {

        var setupLearnerProfile = function (profileData) {

            var learnerProfileElement = $('.learner-profile-container');
            var learnerProfileModel = new LearnerProfileModel();
            learnerProfileModel.url = learnerProfileElement.data('profile-api-url');

            var learnerProfileView = new LearnerProfileView({
                el: learnerProfileElement,
                model: learnerProfileModel,
                learnerProfileModelUrl: learnerProfileModel.url,
                accountSettingsPageUrl: learnerProfileElement.data('account-settings-page-url'),
                profileData: profileData,
                // pass profile photo view here.

            });

            // TODO! Fetch values into model once profile API is available
            learnerProfileView.render();
        };

        return setupLearnerProfile;
    })
}).call(this, define || RequireJS.define);