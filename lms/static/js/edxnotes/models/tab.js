;(function (define, undefined) {
'use strict';
define(['backbone'], function (Backbone) {
    var TabModel = Backbone.Model.extend({
        defaults: {
            'name': '',
            'class_name': '',
            'is_active': false,
            'is_closable': false
        }
    });

    return TabModel;
});
}).call(this, define || RequireJS.define);
