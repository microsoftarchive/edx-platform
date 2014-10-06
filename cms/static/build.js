({
    paths: {
        "domReady": "js/vendor/domReady",
        "gettext": "empty:",
        "mustache": "js/vendor/mustache",
        "codemirror": "js/vendor/codemirror-compressed",
        "codemirror/stex": "js/vendor/CodeMirror/stex",
        "jquery": "js/vendor/jquery.min",
        "jquery.ui": "js/vendor/jquery-ui.min",
        "jquery.form": "js/vendor/jquery.form",
        "jquery.markitup": "js/vendor/markitup/jquery.markitup",
        "jquery.leanModal": "js/vendor/jquery.leanModal.min",
        "jquery.ajaxQueue": "js/vendor/jquery.ajaxQueue",
        "jquery.smoothScroll": "js/vendor/jquery.smooth-scroll.min",
        "jquery.timepicker": "js/vendor/timepicker/jquery.timepicker",
        "jquery.cookie": "js/vendor/jquery.cookie",
        "jquery.qtip": "js/vendor/jquery.qtip.min",
        "jquery.scrollTo": "js/vendor/jquery.scrollTo-1.4.2-min",
        "jquery.flot": "js/vendor/flot/jquery.flot.min",
        "jquery.fileupload": "js/vendor/jQuery-File-Upload/js/jquery.fileupload",
        "jquery.iframe-transport": "js/vendor/jQuery-File-Upload/js/jquery.iframe-transport",
        "jquery.inputnumber": "js/vendor/html5-input-polyfills/number-polyfill",
        "jquery.immediateDescendents": "coffee/src/jquery.immediateDescendents",
        "datepair": "js/vendor/timepicker/datepair",
        "date": "js/vendor/date",
        "tzAbbr": "js/vendor/tzAbbr",
        "underscore": "js/vendor/underscore-min",
        "underscore.string": "js/vendor/underscore.string.min",
        "backbone": "js/vendor/backbone-min",
        "backbone.associations": "js/vendor/backbone-associations-min",
        "backbone.paginator": "js/vendor/backbone.paginator.min",
        "tinymce": "js/vendor/tinymce/js/tinymce/tinymce.full.min",
        "jquery.tinymce": "js/vendor/tinymce/js/tinymce/jquery.tinymce.min",
        "xmodule": "empty:",
        "xblock": "coffee/src/xblock",
        "utility": "js/src/utility",
        "accessibility": "js/src/accessibility_tools",
        "draggabilly": "js/vendor/draggabilly.pkgd",
        "URI": "js/vendor/URI.min",
        "ieshim": "js/src/ie_shim",
        "tooltip_manager": "js/src/tooltip_manager",

        // Files needed for Annotations feature
        "annotator": "js/vendor/ova/annotator-full",
        "annotator-harvardx": "js/vendor/ova/annotator-full-firebase-auth",
        "video.dev": "js/vendor/ova/video.dev",
        "vjs.youtube": 'js/vendor/ova/vjs.youtube',
        "rangeslider": 'js/vendor/ova/rangeslider',
        "share-annotator": 'js/vendor/ova/share-annotator',
        "richText-annotator": 'js/vendor/ova/richText-annotator',
        "reply-annotator": 'js/vendor/ova/reply-annotator',
        "grouping-annotator": 'js/vendor/ova/grouping-annotator',
        "tags-annotator": 'js/vendor/ova/tags-annotator',
        "diacritic-annotator": 'js/vendor/ova/diacritic-annotator',
        "flagging-annotator": 'js/vendor/ova/flagging-annotator',
        "jquery-Watch": 'js/vendor/ova/jquery-Watch',
        "openseadragon": 'js/vendor/ova/openseadragon',
        "osda": 'js/vendor/ova/OpenSeaDragonAnnotation',
        "ova": 'js/vendor/ova/ova',
        "catch": 'js/vendor/ova/catch/js/catch',
        "handlebars": 'js/vendor/ova/catch/js/handlebars-1.1.2',
        // end of Annotation tool files
        "mathjax": "empty:",
        "tender": "empty:",
        "youtube": "empty:"
    },
    shim: {
        "date": {
            exports: "Date"
        },
        "jquery.ui": {
            deps: ["jquery"],
            exports: "jQuery.ui"
        },
        "jquery.form": {
            deps: ["jquery"],
            exports: "jQuery.fn.ajaxForm"
        },
        "jquery.markitup": {
            deps: ["jquery"],
            exports: "jQuery.fn.markitup"
        },
        "jquery.leanmodal": {
            deps: ["jquery"],
            exports: "jQuery.fn.leanModal"
        },
        "jquery.ajaxQueue": {
            deps: ["jquery"],
            exports: "jQuery.fn.ajaxQueue"
        },
        "jquery.smoothScroll": {
            deps: ["jquery"],
            exports: "jQuery.fn.smoothScroll"
        },
        "jquery.cookie": {
            deps: ["jquery"],
            exports: "jQuery.fn.cookie"
        },
        "jquery.qtip": {
            deps: ["jquery"],
            exports: "jQuery.fn.qtip"
        },
        "jquery.scrollTo": {
            deps: ["jquery"],
            exports: "jQuery.fn.scrollTo",
        },
        "jquery.flot": {
            deps: ["jquery"],
            exports: "jQuery.fn.plot"
        },
        "jquery.fileupload": {
            deps: ["jquery.iframe-transport"],
            exports: "jQuery.fn.fileupload"
        },
        "jquery.inputnumber": {
            deps: ["jquery"],
            exports: "jQuery.fn.inputNumber"
        },
        "jquery.tinymce": {
            deps: ["jquery", "tinymce"],
            exports: "jQuery.fn.tinymce"
        },
        "datepair": {
            deps: ["jquery.ui", "jquery.timepicker"]
        },
        "underscore": {
            exports: "_"
        },
        "backbone": {
            deps: ["underscore", "jquery"],
            exports: "Backbone"
        },
        "backbone.associations": {
            deps: ["backbone"],
            exports: "Backbone.Associations"
        },
        "backbone.paginator": {
            deps: ["backbone"],
            exports: "Backbone.Paginator"
        },
        "codemirror": {
            exports: "CodeMirror"
        },
        "codemirror/stex": {
            deps: ["codemirror"]
        },
        "tinymce": {
            exports: "tinymce"
        },
        "URI": {
            exports: "URI"
        },
        "tooltip_manager": {
            deps: ["jquery", "underscore"]
        },
        "jquery.immediateDescendents": {
            deps: ["jquery"]
        },
        "xblock/core": {
            exports: "XBlock",
            deps: ["jquery", "jquery.immediateDescendents"]
        },
        "xmodule": {
            deps: [
                "jquery", "underscore", "mathjax", "codemirror", "tinymce",
                "jquery.tinymce", "jquery.qtip", "jquery.scrollTo", "jquery.flot",
                "jquery.cookie",
                "utility"
            ]
        },
        "xblock/runtime.v1": {
            exports: "XBlock",
            deps: ["xblock/core", "jquery.immediateDescendents"]
        },

        "coffee/src/main": {
            deps: ["coffee/src/ajax_prefix"]
        },
        "coffee/src/logger": {
            exports: "Logger",
            deps: ["coffee/src/ajax_prefix"]
        },

        // the following are all needed for annotation tools
        "video.dev": {
            exports:"videojs"
        },
        "vjs.youtube": {
            deps: ["video.dev"]
        },
        "rangeslider": {
            deps: ["video.dev"]
        },
        "annotator": {
            exports: "Annotator"
        },
        "annotator-harvardx":{
            deps: ["annotator"]
        },
        "share-annotator": {
            deps: ["annotator"]
        },
        "richText-annotator": {
            deps: ["annotator", "tinymce"]
        },
        "reply-annotator": {
            deps: ["annotator"]
        },
        "tags-annotator": {
            deps: ["annotator"]
        },
        "diacritic-annotator": {
            deps: ["annotator"]
        },
        "flagging-annotator": {
            deps: ["annotator"]
        },
        "grouping-annotator": {
            deps: ["annotator"]
        },
        "ova":{
            exports: "ova",
            deps: ["annotator", "annotator-harvardx", "video.dev", "vjs.youtube", "rangeslider", "share-annotator", "richText-annotator", "reply-annotator", "tags-annotator", "flagging-annotator", "grouping-annotator", "diacritic-annotator", "jquery-Watch", "catch", "handlebars", "URI"]
        },
        "osda":{
            exports: "osda",
            deps: ["annotator", "annotator-harvardx", "video.dev", "vjs.youtube", "rangeslider", "share-annotator", "richText-annotator", "reply-annotator", "tags-annotator", "flagging-annotator", "grouping-annotator", "diacritic-annotator", "openseadragon", "jquery-Watch", "catch", "handlebars", "URI"]
        },
        // end of annotation tool files
    },
    waitSeconds: 60,
    skipDirOptimize: true,
    optimizeCss: "none",
    modules: [
        {name: 'js/require_pages/base'},
        {name: 'js/require_pages/index', exclude: ["backbone", "jquery", "underscore"]}, // Home
        {name: 'js/require_pages/course', exclude: ["backbone", "jquery", "underscore"]}, // Course
        {name: 'js/require_pages/login', exclude: ["backbone", "jquery", "underscore"]}, // Login
        {name: 'js/require_pages/outline', exclude: ["backbone", "jquery", "underscore"]}, // Outline
        {name: 'js/require_pages/container', exclude: ["backbone", "jquery", "underscore"]} // Container
    ]
})
