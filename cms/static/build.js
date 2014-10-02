({
    //The top level directory that contains your app. If this option is used
    //then it assumed your scripts are in a subdirectory under this path.
    //This option is not required. If it is not specified, then baseUrl
    //below is the anchor point for finding things. If this option is specified,
    //then all the files from the app directory will be copied to the dir:
    //output area, and baseUrl will assume to be a relative path under
    //this directory.
    appDir: "./",

    //By default, all modules are located relative to this path. If baseUrl
    //is not explicitly set, then all modules are loaded relative to
    //the directory that holds the build file. If appDir is set, then
    //baseUrl should be specified as relative to the appDir.
    baseUrl: "./",
    //Set paths for modules. If relative paths, set relative to baseUrl above.
    //If a special value of "empty:" is used for the path value, then that
    //acts like mapping the path to an empty file. It allows the optimizer to
    //resolve the dependency to path, but then does not include it in the output.
    //Useful to map module names that are to resources on a CDN or other
    //http: URL when running in the browser and during an optimization that
    //file should be skipped because it has no dependencies.
    paths: {
        "domReady": "xmodule_js/common_static/js/vendor/domReady",
        "gettext": "js/i18n",
        "mustache": "xmodule_js/common_static/js/vendor/mustache",
        "codemirror": "xmodule_js/common_static/js/vendor/codemirror-compressed",
        "codemirror/stex": "xmodule_js/common_static/js/vendor/CodeMirror/stex",
        "jquery": "xmodule_js/common_static/js/vendor/jquery.min",
        "jquery.ui": "xmodule_js/common_static/js/vendor/jquery-ui.min",
        "jquery.form": "xmodule_js/common_static/js/vendor/jquery.form",
        "jquery.markitup": "xmodule_js/common_static/js/vendor/markitup/jquery.markitup",
        "jquery.leanModal": "xmodule_js/common_static/js/vendor/jquery.leanModal.min",
        "jquery.ajaxQueue": "xmodule_js/common_static/js/vendor/jquery.ajaxQueue",
        "jquery.smoothScroll": "xmodule_js/common_static/js/vendor/jquery.smooth-scroll.min",
        "jquery.timepicker": "xmodule_js/common_static/js/vendor/timepicker/jquery.timepicker",
        "jquery.cookie": "xmodule_js/common_static/js/vendor/jquery.cookie",
        "jquery.qtip": "xmodule_js/common_static/js/vendor/jquery.qtip.min",
        "jquery.scrollTo": "xmodule_js/common_static/js/vendor/jquery.scrollTo-1.4.2-min",
        "jquery.flot": "xmodule_js/common_static/js/vendor/flot/jquery.flot.min",
        "jquery.fileupload": "xmodule_js/common_static/js/vendor/jQuery-File-Upload/js/jquery.fileupload",
        "jquery.iframe-transport": "xmodule_js/common_static/js/vendor/jQuery-File-Upload/js/jquery.iframe-transport",
        "jquery.inputnumber": "xmodule_js/common_static/js/vendor/html5-input-polyfills/number-polyfill",
        "jquery.immediateDescendents": "xmodule_js/common_static/coffee/src/jquery.immediateDescendents",
        "datepair": "xmodule_js/common_static/js/vendor/timepicker/datepair",
        "date": "xmodule_js/common_static/js/vendor/date",
        "tzAbbr": "xmodule_js/common_static/js/vendor/tzAbbr",
        "underscore": "xmodule_js/common_static/js/vendor/underscore-min",
        "underscore.string": "xmodule_js/common_static/js/vendor/underscore.string.min",
        "backbone": "xmodule_js/common_static/js/vendor/backbone-min",
        "backbone.associations": "xmodule_js/common_static/js/vendor/backbone-associations-min",
        "backbone.paginator": "xmodule_js/common_static/js/vendor/backbone.paginator.min",
        "tinymce": "xmodule_js/common_static/js/vendor/tinymce/js/tinymce/tinymce.full.min",
        "jquery.tinymce": "xmodule_js/common_static/js/vendor/tinymce/js/tinymce/jquery.tinymce.min",
        "xmodule": "xmodule_js/src/xmodule",
        "xblock": "xmodule_js/common_static/coffee/src/xblock",
        "utility": "xmodule_js/common_static/js/src/utility",
        "accessibility": "xmodule_js/common_static/js/src/accessibility_tools",
        "draggabilly": "xmodule_js/common_static/js/vendor/draggabilly.pkgd",
        "URI": "xmodule_js/common_static/js/vendor/URI.min",
        "ieshim": "xmodule_js/common_static/js/src/ie_shim",
        "tooltip_manager": "xmodule_js/common_static/js/src/tooltip_manager",

        // Files needed for Annotations feature
        "annotator": "xmodule_js/common_static/js/vendor/ova/annotator-full",
        "annotator-harvardx": "xmodule_js/common_static/js/vendor/ova/annotator-full-firebase-auth",
        "video.dev": "xmodule_js/common_static/js/vendor/ova/video.dev",
        "vjs.youtube": 'xmodule_js/common_static/js/vendor/ova/vjs.youtube',
        "rangeslider": 'xmodule_js/common_static/js/vendor/ova/rangeslider',
        "share-annotator": 'xmodule_js/common_static/js/vendor/ova/share-annotator',
        "richText-annotator": 'xmodule_js/common_static/js/vendor/ova/richText-annotator',
        "reply-annotator": 'xmodule_js/common_static/js/vendor/ova/reply-annotator',
        "grouping-annotator": 'xmodule_js/common_static/js/vendor/ova/grouping-annotator',
        "tags-annotator": 'xmodule_js/common_static/js/vendor/ova/tags-annotator',
        "diacritic-annotator": 'xmodule_js/common_static/js/vendor/ova/diacritic-annotator',
        "flagging-annotator": 'xmodule_js/common_static/js/vendor/ova/flagging-annotator',
        "jquery-Watch": 'xmodule_js/common_static/js/vendor/ova/jquery-Watch',
        "openseadragon": 'xmodule_js/common_static/js/vendor/ova/openseadragon',
        "osda": 'xmodule_js/common_static/js/vendor/ova/OpenSeaDragonAnnotation',
        "ova": 'xmodule_js/common_static/js/vendor/ova/ova',
        "catch": 'xmodule_js/common_static/js/vendor/ova/catch/js/catch',
        "handlebars": 'xmodule_js/common_static/js/vendor/ova/catch/js/handlebars-1.1.2',
        // end of Annotation tool files

        // // externally hosted files
        // "tender": [
        //     "//edxedge.tenderapp.com/tender_widget",
        //     // if tender fails to load, fallback on a local file
        //     // so that require doesn't fall over
        //     "js/src/tender_fallback"
        // ],
        // "mathjax": "//edx-static.s3.amazonaws.com/mathjax-MathJax-727332c/MathJax.js?config=TeX-MML-AM_HTMLorMML-full&delayStartupUntil=configured",
        // "youtube": [
        //     // youtube URL does not end in ".js". We add "?noext" to the path so
            // that require.js adds the ".js" to the query component of the URL,
            // and leaves the path component intact.
            // "//www.youtube.com/player_api?noext",
            // // if youtube fails to load, fallback on a local file
            // // so that require doesn't fall over
            // "js/src/youtube_fallback"
        // ]
    },
    shim: {
        "gettext": {
            exports: "gettext"
        },
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
        // "tender": {
        //     exports: 'Tender'
        // },
        // "youtube": {
        //     exports: "YT"
        // },
        "codemirror": {
            exports: "CodeMirror"
        },
        "codemirror/stex": {
            deps: ["codemirror"]
        },
        "tinymce": {
            exports: "tinymce"
        },
        "mathjax": {
            exports: "MathJax",
            init: function() {
              MathJax.Hub.Config({
                tex2jax: {
                  inlineMath: [
                    ["\\(","\\)"],
                    ['[mathjaxinline]','[/mathjaxinline]']
                  ],
                  displayMath: [
                    ["\\[","\\]"],
                    ['[mathjax]','[/mathjax]']
                  ]
                }
              });
              MathJax.Hub.Configured();
            }
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
        "xblock/runtime.v1": {
            exports: "XBlock",
            deps: ["xblock/core"]
        },

        "coffee/src/main": {
            deps: ["xmodule_js/common_static/coffee/src/ajax_prefix"]
        },
        "coffee/src/logger": {
            exports: "Logger",
            deps: ["xmodule_js/common_static/coffee/src/ajax_prefix"]
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

    map: {
        "*": {
            "coffee/src/ajax_prefix": "xmodule_js/common_static/coffee/src/ajax_prefix",
            "coffee/src/logger": "xmodule_js/common_static/coffee/src/logger",
            "xblock/cms.runtime.v1": "coffee/src/xblock/cms.runtime.v1",
            "xblock/core": "xmodule_js/common_static/coffee/src/xblock/core"
        }
    },

    deps: ["jquery"],

    dir: "../build",
    waitSeconds: 60,
    findNestedDependencies: true,
    // optimize: "none",
    modules: [
        {name: 'js/require_pages/base'},
        {name: 'js/require_pages/course', exclude: ["backbone", "jquery", "underscore"]}, // Course
        {name: 'js/require_pages/index', exclude: ["backbone", "jquery", "underscore"]}, // Course
        {name: 'js/require_pages/login', exclude: ["backbone", "jquery", "underscore"]}, // Login
        {name: 'js/require_pages/outline', exclude: ["backbone", "jquery", "underscore"]}, // Outline
        {name: 'js/require_pages/container', exclude: ["backbone", "jquery", "underscore"]} // Container
        // {name: 'js/require_pages/container'}, // Advanced Settings
    ]
})
