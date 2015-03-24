/**
 * View for in-course reverification.
 *
 * This view is responsible for rendering the page
 * template, including any subviews (for photo capture).
 */
 var edx = edx || {};

(function( $, _, Backbone, gettext ) {
    'use strict';

    edx.verify_student = edx.verify_student || {};

    edx.verify_student.InCourseReverifyView = Backbone.View.extend({
        el: '#incourse-reverify-container',
        templateId: '#incourse_reverify-tpl',
        submitButtonId: '#submit',

        initialize: function( obj ) {
            this.errorModel = obj.errorModel || null;
            this.courseKey = obj.courseKey || null;
            this.checkpointName = obj.checkpointName || null;

            this.model = new edx.verify_student.ReverificationModel({
                courseKey: this.courseKey,
                checkpointName: this.checkpointName
            });

            this.listenTo( this.model, 'sync', _.bind( this.handleSubmitPhotoSuccess, this ));
            this.listenTo( this.model, 'error', _.bind( this.handleSubmissionError, this ));
        },

        render: function() {
            var renderedTemplate = _.template(
                $( this.templateId ).html(),
                {
                    courseKey: this.courseKey,
                    checkpointName: this.checkpointName
                }
            );
            $( this.el ).html( renderedTemplate );
            $( this.submitButtonId ).on( 'click', _.bind( this.submitPhoto, this ));

            // Render the webcam view *after* the parent view
            // so that the container div for the webcam
            // exists in the DOM.
            this.renderWebcam();

            return this;
        },

        renderWebcam: function() {
            edx.verify_student.getSupportedWebcamView({
                el: $( '#webcam' ),
                model: this.model,
                modelAttribute: 'faceImage',
                submitButton: this.submitButtonId,
                errorModel: this.errorModel
            }).render();
        },

        submitPhoto: function() {
            // TODO: disable the submit button to prevent multiple submissions.
            this.model.save();
        },

        handleSubmitPhotoSuccess: function() {
            // TODO: redirect back to a URL returned by the server.
            // Eventually this will be a redirect back into the courseware,
            // but for now we can return to the student dashboard.
            console.log('Submitted');
        },

        handleSubmissionError: function() {
            // TODO: use `this.errorModel` to display the error
            // (see the webcam view for an example)
            // TODO: Re-enable the submit button to allow the
            // user to resubmit.
            console.log('Error!');
        }
    });
})( jQuery, _, Backbone, gettext );
