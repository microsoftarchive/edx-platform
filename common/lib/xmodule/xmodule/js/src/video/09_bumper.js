(function (define) {

// VideoCaption module.
define(
'video/09_bumper.js',
['video/01_initialize.js'],
function (initialize) {
    /**
     * @desc VideoCaption module exports a function.
     *
     * @type {function}
     * @access public
     *
     * @param {object} state - The object containing the state of the video
     *     player. All other modules, their parameters, public variables, etc.
     *     are available via this object.
     *
     * @this {object} The global window object.
     *
     * @returns {jquery Promise}
     */
    var VideoBumper = function (state, element) {
        if (!(this instanceof VideoBumper)) {
            return new VideoBumper(state, element);
        }

        this.dfd = $.Deferred();
        this.element = element;
        this.state = state;
        this.state.videoBumper = this;
        this.renderElements();
        this.bindHandlers();
        this.initialize();
        return this.dfd.promise();
    };

    VideoBumper.prototype = {
        initialize: function () {
            this.controls = $('.video-controls', this.state.el).clone();
            this.state = $.extend(true, {}, this.state, {
                // videoType: 'html5',
                metadata: {
                    savedVideoPosition: 0,
                    speed: '1.0',
                    startTime: 0,
                    endTime: null,
                    streams: [],
                    sources: ['http://www.w3schools.com/html/mov_bbb.mp4']
                }
            });

            this.state.modules = this.state.bumper_modules;
            initialize(this.state, this.element);
        },

        /**
        * @desc Initiate rendering of elements, and set their initial configuration.
        *
        */
        renderElements: function () {
            var state = this.state;
            $('.add-fullscreen, .volume, .speeds, .slider', state.el).css('visibility', 'hidden');
        },

        /**
        * @desc Bind any necessary function callbacks to DOM events (click,
        *     mousemove, etc.).
        *
        */
        bindHandlers: function () {
            this.state.el.on('ended', this.onDone.bind(this));
        },

        canShowVideo: function () {
            return this.dfd.resolve();
        },

        onDone: function () {
            var state = this.state;
            if (state.videoPlayer.player.destroy) {
                state.videoPlayer.player.destroy();
            } else {
                $('video', state.el).remove();
            }

            $('.video-controls', this.state.el).replaceWith(this.controls);
            this.dfd.resolve();
        }
    };

    return VideoBumper;
});

}(RequireJS.define));
