;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone'
    ], function (gettext, $, _, Backbone) {

        var MessageBannerView = Backbone.View.extend({

            templateSelector: '#message_banner-tpl',

            initialize: function (options) {
                this.template = _.template($(this.templateSelector).text());
            },

            render: function () {
                this.$el.html(this.template({
                    message: this.options.message
                }));
                return this;
            }
        });

        return MessageBannerView;
    })
}).call(this, define || RequireJS.define);
