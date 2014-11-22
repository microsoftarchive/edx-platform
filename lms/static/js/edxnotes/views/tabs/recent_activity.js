;(function (define, undefined) {
'use strict';
define([
    'gettext', 'js/edxnotes/views/tab_view', 'js/edxnotes/views/subview'
], function (gettext, TabView, SubView) {
    var RecentActivityView = TabView.extend({

        SubViewConstructor: SubView.extend({
            id: 'edx-notes-page-recent-activity'
        }),

        tabInfo: {
            name: gettext('Recent Activity'),
            class_name: 'tab-recent-activity'
        }
    });

    return RecentActivityView;
});
}).call(this, define || RequireJS.define);
