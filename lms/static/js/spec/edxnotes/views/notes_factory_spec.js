define([
    'annotator', 'js/edxnotes/views/notes_factory', 'js/common_helpers/ajax_helpers',
    'js/spec/edxnotes/custom_matchers'
], function(Annotator, NotesFactory, AjaxHelpers, customMatchers) {
    'use strict';
    var B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        base64Encode, makeToken;

    base64Encode = function (data) {
        var ac, bits, enc, h1, h2, h3, h4, i, o1, o2, o3, r, tmp_arr;
        if (btoa) {
            // Gecko and Webkit provide native code for this
            return btoa(data);
        } else {
            // Adapted from MIT/BSD licensed code at http://phpjs.org/functions/base64_encode
            // version 1109.2015
            i = 0;
            ac = 0;
            enc = "";
            tmp_arr = [];
            if (!data) {
                return data;
            }
            data += '';
            while (i < data.length) {
                o1 = data.charCodeAt(i++);
                o2 = data.charCodeAt(i++);
                o3 = data.charCodeAt(i++);
                bits = o1 << 16 | o2 << 8 | o3;
                h1 = bits >> 18 & 0x3f;
                h2 = bits >> 12 & 0x3f;
                h3 = bits >> 6 & 0x3f;
                h4 = bits & 0x3f;
                tmp_arr[ac++] = B64.charAt(h1) + B64.charAt(h2) + B64.charAt(h3) + B64.charAt(h4);
            }
            enc = tmp_arr.join('');
            r = data.length % 3;
            return (r ? enc.slice(0, r - 3) : enc) + '==='.slice(r || 3);
        }
    };

    makeToken = function() {
        var now = (new Date()).getTime() / 1000,
            rawToken = {
                sub: "sub",
                exp: now + 100,
                iat: now
            };

        return 'header.' + base64Encode(JSON.stringify(rawToken)) + '.signature';
    };

    describe('EdxNotes NotesFactory', function() {
        var wrapper;

        beforeEach(function() {
            customMatchers(this);
            loadFixtures('js/fixtures/edxnotes/edxnotes_wrapper.html');
            this.wrapper = document.getElementById('edx-notes-wrapper-123');
        });

        afterEach(function () {
            _.invoke(Annotator._instances, 'destroy');
        });

        it('can initialize annotator correctly', function() {
            var requests = AjaxHelpers.requests(this),
                token = makeToken(),
                options = {
                    user: 'a user',
                    usage_id : 'an usage',
                    course_id: 'a course'
                },
                annotator = NotesFactory.factory(this.wrapper, {
                    endpoint: '/test_endpoint',
                    user: 'a user',
                    usageId : 'an usage',
                    courseId: 'a course',
                    token: token,
                    tokenUrl: '/test_token_url'
                }),
                request = requests[0];

            expect(requests).toHaveLength(1);
            expect(request.requestHeaders['x-annotator-auth-token']).toBe(token);
            expect(annotator.options.auth.tokenUrl).toBe('/test_token_url');
            expect(annotator.options.store.prefix).toBe('/test_endpoint');
            expect(annotator.options.store.annotationData).toEqual(options);
            expect(annotator.options.store.loadFromSearch).toEqual(options);
        });
    });
});
