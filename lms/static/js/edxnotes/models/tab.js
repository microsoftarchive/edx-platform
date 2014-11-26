;(function (define, undefined) {
'use strict';
define(['backbone'], function (Backbone) {
    var TabModel = Backbone.Model.extend({
        defaults: {
            'name': '',
            'class_name': '',
            'is_active': false,
            'is_closable': false
        },

        activate: function () {
            this.collection.each(_.bind(function(model) {
                // Unactivate all other models.
                if (model !== this) {
                    model.unactivate();
                }
            }, this));
            this.set('is_active', true);
        },

        unactivate: function () {
            this.set('is_active', false);
        },

        isActive: function () {
            return this.get('is_active');
        }
    });

    return TabModel;
});
}).call(this, define || RequireJS.define);
