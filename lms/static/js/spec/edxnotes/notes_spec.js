define(['jquery', 'annotator', 'jasmine-jquery'],
    function($, Annotator) {
        'use strict';

        describe('Test notes', function() {
            var wrapper;

            beforeEach(function() {
                loadFixtures('js/fixtures/edxnotes/edxnotes.html');
                wrapper = $('div#edx-notes-wrapper-123');
            });

            it('Tests if fixture has been loaded', function() {
                expect(wrapper).toExist();
                expect(wrapper).toHaveClass('edx-notes-wrapper');
                // This fails, why?
                expect(Annotator).not.toBeUndefined();
            });
        });
    }
);
