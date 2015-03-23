;(function (define) {

define([
    'jquery',
    'underscore',
    'backbone',
    'gettext'
], function ($, _, Backbone, gettext) {
    'use strict';

    return Backbone.View.extend({

        tagName: 'li',
        templateId: '',
        className: 'search-results-item',
        attributes: {
            'role': 'region',
            'aria-label': 'search result'
        },

        initialize: function () {
            this.tpl = _.template($(this.templateId).html());
        },

        render: function () {
            var data = _.clone(this.model.attributes);
            // Drop the preview text and result type if the search term is found
            //  in the title/location in the course hierarchy
            if (this.model.get('content_type') === 'Sequence') {
                data.excerpt = '';
                data.content_type = '';
            }
            this.$el.html(this.tpl(data));
            return this;
        }
    });

});

})(define || RequireJS.define);
