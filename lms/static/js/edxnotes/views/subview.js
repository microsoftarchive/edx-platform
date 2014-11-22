;(function (define, undefined) {
'use strict';
define(['underscore', 'backbone', 'js/edxnotes/views/note_item'],
function (_, Backbone, NoteItemView) {
    var SubView = Backbone.View.extend({
        className: 'edx-notes-page-items-list',

        render: function () {
            this.items = this.collection.map(function(model) {
                var item = new NoteItemView({
                    model: model
                }).render();
                item.$el.appendTo(this.$el);
                return item;
            }, this);

            return this;
        },

        destroy: function () {
            // Removes a view from the DOM, and calls stopListening to remove
            // any bound events that the view has listenTo'd.
            this.remove();
            // Destroy all children.
            _.invoke(this.items, 'destroy');
            delete this.items;
        }
    });

    return SubView;
});
}).call(this, define || RequireJS.define);
