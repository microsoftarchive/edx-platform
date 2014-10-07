define([
    'domReady!', 'jquery', 'js/views/settings/grading', 'js/models/settings/course_grading_policy'
], function(doc, $, GradingView, CourseGradingPolicyModel) {
    'use strict';
    return function (courseDetails, gradingUrl) {
        var model, editor;

        $('form :input')
            .focus(function() {
                $('label[for="' + this.id + '"]').addClass('is-focused');
            })
            .blur(function() {
                $('label').removeClass('is-focused');
            });

        model = new CourseGradingPolicyModel(courseDetails,{parse:true});
        model.urlRoot = gradingUrl;
        editor = new GradingView({
            el: $('.settings-grading'),
            model : model
        });
        editor.render();
    };
});
