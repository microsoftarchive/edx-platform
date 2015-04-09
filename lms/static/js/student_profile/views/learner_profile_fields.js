;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'js/views/fields', 'backbone-super'
    ], function (gettext, $, _, Backbone, FieldViews) {

        var LearnerProfileFieldViews = {};

        LearnerProfileFieldViews.AccountPrivacyFieldView = FieldViews.DropdownFieldView.extend({

            render: function () {
                this._super();
                this.message();
                this.updateFieldValue();
                return this;
            },

            message: function () {
                if (this.profileIsPrivate) {
                    this._super(interpolate_text(
                        gettext("You must specify your birth year before you can share your full profile. To specify your birth year, go to the {account_settings_page_link}"),
                        {'account_settings_page_link': '<a href="' + this.options.accountSettingsPageUrl + '">' + gettext('Account Settings page.') + '</a>'}
                    ));
                } else if (this.requiresParentalConsent) {
                    this._super(interpolate_text(
                        gettext('You must be over 13 to share a full profile. If you are over 13, make sure that you have specified a birth year on the {account_settings_page_link}'),
                        {'account_settings_page_link': '<a href="' + this.options.accountSettingsPageUrl + '">' + gettext('Account Settings page.') + '</a>'}
                    ));
                }
                else {
                    this._super('');
                }
                return this._super();
            },

            updateFieldValue: function() {
                if (!this.isAboveMinimumAge) {
                    this.$('.u-field-value select').val('private');
                    this.disableField(true);
                }
            }
        });

        LearnerProfileFieldViews.ProfileImageFieldView = FieldViews.ImageFieldView.extend({

            imageUrl: function () {
                return this.model.profileImageUrl();
            },

            imageAltText: function () {
                return gettext("Profile photo for " + this.model.get('username'));
            },

            uploadButtonTitle: function () {
                if (this.model.hasProfileImage()) {
                    return _.result(this, 'titleEdit')
                } else {
                    return _.result(this, 'titleAdd')
                }
            },

            imageChangeSucceeded: function (e, data) {
                var view = this;
                // Update model to get the latest urls of profile image.
                this.model.fetch().done(function () {
                    view.setCurrentStatus('');
                }).fail(function () {
                    view.showMessage(view.errorMessage);
                });
            },

            showMessage: function (message) {
                this.options.messageView.showMessage(message);
            },

            hideMessage: function () {
                this.options.messageView.hideMessage();
            },

            setUploadButtonVisibility: function (state) {
                this.$('.u-field-upload-button').css('display', state);
            },

            setRemoveButtonVisibility: function (state) {
                this.$('.u-field-remove-button').css('display', state);
            },

            setElementVisibility: function (state) {
                if (!this.model.isAboveMinimumAge()) {
                    this.setUploadButtonVisibility(state);
                }

                if (!this.model.hasProfileImage()) {
                    this.$('.u-field-remove-button').css('display', state);
                }

                if(this.inProgress() ||  this.options.editable === 'never') {
                    this.setUploadButtonVisibility(state);
                    this.setRemoveButtonVisibility(state);
                }
            },

        });

        return LearnerProfileFieldViews;
    })
}).call(this, define || RequireJS.define);
