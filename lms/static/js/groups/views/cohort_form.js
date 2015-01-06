var edx = edx || {};

(function($, _, Backbone, gettext, interpolate_text, CohortModel, NotificationModel, NotificationView) {
    'use strict';

    edx.groups = edx.groups || {};

    edx.groups.CohortFormView = Backbone.View.extend({
        events : {
            'change .cohort-management-details-association-course input': 'onRadioButtonChange',
            'click .tab-content-settings .action-save': 'saveSettings',
            'submit .cohort-management-group-add-form': 'addStudents'
        },

        initialize: function(options) {
            this.template = _.template($('#cohort-form-tpl').text());
            this.contentGroups = options.contentGroups;
            this.context = options.context;
        },

        showNotification: function(options, beforeElement) {
            var model = new NotificationModel(options);
            this.removeNotification();
            this.notification = new NotificationView({
                model: model
            });
            this.notification.render();
            beforeElement.before(this.notification.$el);
        },

        removeNotification: function() {
            if (this.notification) {
                this.notification.remove();
            }
        },

        render: function() {
            this.$el.html(this.template({
                cohort: this.model,
                contentGroups: this.contentGroups,
                studioGroupConfigurationsUrl: this.context.studioGroupConfigurationsUrl
            }));
            return this;
        },

        onRadioButtonChange: function(event) {
            var target = $(event.currentTarget),
                groupsEnabled = target.val() === 'yes';
            if (!groupsEnabled) {
                // If the user has chosen 'no', then clear the selection by setting
                // it to the first option which represents no selection.
                this.$('.input-cohort-group-association').val('None');
            }
            // Enable the select if the user has chosen groups, else disable it
            this.$('.input-cohort-group-association').prop('disabled', !groupsEnabled);
        },

        hasAssociatedContentGroup: function() {
            return this.$('.radio-yes').prop('checked');
        },

        getSelectedContentGroup: function() {
            var selectValue = this.$('.input-cohort-group-association').val(),
                ids, groupId, userPartitionId, i, contentGroup;
            if (!this.hasAssociatedContentGroup() || selectValue === 'None') {
                return null;
            }
            ids = selectValue.split(':');
            groupId = parseInt(ids[0]);
            userPartitionId = parseInt(ids[1]);
            for (i=0; i < this.contentGroups.length; i++) {
                contentGroup = this.contentGroups[i];
                if (contentGroup.get('id') === groupId && contentGroup.get('user_partition_id') === userPartitionId) {
                    return contentGroup;
                }
            }
            return null;
        },

        getUpdatedCohortName: function() {
            var cohortName = this.$('.cohort-name').val();
            return cohortName ? cohortName.trim() : this.model.get('name');
        },

        showMessage: function(message, type, details) {
            this.showNotification(
                {type: type || 'confirmation', title: message, details: details},
                this.$('.form-fields')
            );
        },

        validateForm: function() {
            var errorMessages, cohortName, selectedContentGroup;
            errorMessages = [];
            cohortName = this.getUpdatedCohortName();
            selectedContentGroup = this.getSelectedContentGroup();
            if (cohortName.length === 0) {
                errorMessages.push(gettext('You must specify a name for the cohort group'));
            }
            if (this.hasAssociatedContentGroup() && !selectedContentGroup) {
                if (this.$('.input-cohort-group-association').val() === 'None') {
                    errorMessages.push(gettext('You did not select a cohorted content group'));
                } else {
                    errorMessages.push(gettext('The selected cohorted content group does not exist'));
                }
            }
            return errorMessages;
        },

        saveForm: function() {
            var self = this,
                cohort = this.model,
                saveOperation = $.Deferred(),
                isUpdate = !_.isUndefined(this.model.id),
                cohortName, selectedContentGroup, errorMessages, showErrorMessage;
            showErrorMessage = function(message, details) {
                self.showMessage(message, 'error', details);
            };
            this.removeNotification();
            cohortName = this.getUpdatedCohortName();
            selectedContentGroup = this.getSelectedContentGroup();
            errorMessages = this.validateForm();
            if (errorMessages.length > 0) {
                showErrorMessage(
                    isUpdate ? gettext("The cohort group cannot be saved")
                        : gettext("The cohort group cannot be added"),
                    errorMessages
                );
                saveOperation.reject();
            } else {
                cohort.save(
                    {
                        name: cohortName,
                        group_id: selectedContentGroup ? selectedContentGroup.id : null,
                        user_partition_id: selectedContentGroup ? selectedContentGroup.get('user_partition_id') : null
                    },
                    {patch: isUpdate}
                ).done(function(result) {
                    if (!result.error) {
                        cohort.id = result.id;
                        self.render();    // re-render to remove any now invalid error messages
                        saveOperation.resolve();
                    } else {
                        showErrorMessage(result.error);
                        saveOperation.reject();
                    }
                }).fail(function(result) {
                    var errorMessage = null;
                    try {
                        var jsonResponse = JSON.parse(result.responseText);
                        errorMessage = jsonResponse.error;
                    } catch(e) {
                        // Ignore the exception and show the default error message instead.
                    }
                    if (!errorMessage) {
                        errorMessage = gettext("We've encountered an error. Refresh your browser and then try again.");
                    }
                    showErrorMessage(errorMessage);
                    saveOperation.reject();
                });
            }
            return saveOperation.promise();
        }
    });
}).call(this, $, _, Backbone, gettext, interpolate_text, edx.groups.CohortModel, NotificationModel, NotificationView);
