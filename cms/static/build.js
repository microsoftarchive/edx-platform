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

    //By default all the configuration for optimization happens from the command
    //line or by properties in the config file, and configuration that was
    //passed to requirejs as part of the app's runtime "main" JS file is *not*
    //considered. However, if you prefer the "main" JS file configuration
    //to be read for the build so that you do not have to duplicate the values
    //in a separate configuration, set this property to the location of that
    //main JS file. The first requirejs({}), require({}), requirejs.config({}),
    //or require.config({}) call found in that file will be used.
    //As of 2.1.10, mainConfigFile can be an array of values, with the last
    //value's config take precedence over previous values in the array.
    //mainConfigFile: '../some/path/to/main.js',

    //Set paths for modules. If relative paths, set relative to baseUrl above.
    //If a special value of "empty:" is used for the path value, then that
    //acts like mapping the path to an empty file. It allows the optimizer to
    //resolve the dependency to path, but then does not include it in the output.
    //Useful to map module names that are to resources on a CDN or other
    //http: URL when running in the browser and during an optimization that
    //file should be skipped because it has no dependencies.
    paths: {
        "backbone": "empty:",
        "backbone.associations": "empty:",
        "backbone.paginator": "empty:",
        "codemirror": "empty:",
        "date": "empty:",
        "draggabilly": "empty:",
        "domReady": "empty:",
        "gettext": "empty:",
        "jquery": "empty:",
        "jquery.ajaxQueue": "empty:",
        "jquery.cookie": "empty:",
        "jquery.form": "empty:",
        "jquery.immediateDescendents": "empty:",
        "jquery.inputnumber": "empty:",
        "jquery.smoothScroll": "empty:",
        "jquery.timepicker": "empty:",
        "jquery.ui": "empty:",
        "underscore": "empty:",
        "underscore.string": "empty:",
        "utility": "empty:",
        "xblock": "empty:"
        /*
        "domReady": "xmodule_js/common_static/js/vendor/domReady",
        "gettext": "empty:",
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
        "xmodule": "empty:",
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
        "mathjax": "empty:",
        "tender": "empty:",
        "youtube": "empty:"
        */
    },
    /*
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
    */

    map: {
        "*": {
            "coffee/src/ajax_prefix": "xmodule_js/common_static/coffee/src/ajax_prefix",
            "coffee/src/logger": "xmodule_js/common_static/coffee/src/logger",
            "xblock/cms.runtime.v1": "coffee/src/xblock/cms.runtime.v1",
            "xblock/core": "xmodule_js/common_static/coffee/src/xblock/core"
        }
    },

    //The directory path to save the output. If not specified, then
    //the path will default to be a directory called "build" as a sibling
    //to the build file. All relative paths are relative to the build file.
    dir: "../build",

    //How to optimize all the JS files in the build output directory.
    //Right now only the following values
    //are supported:
    //- "uglify": (default) uses UglifyJS to minify the code.
    //- "uglify2": in version 2.1.2+. Uses UglifyJS2.
    //- "closure": uses Google's Closure Compiler in simple optimization
    //mode to minify the code. Only available if running the optimizer using
    //Java.
    //- "closure.keepLines": Same as closure option, but keeps line returns
    //in the minified files.
    //- "none": no minification will be done.
    //optimize: "none",

    //Introduced in 2.1.2: If using "dir" for an output directory, normally the
    //optimize setting is used to optimize the build bundles (the "modules"
    //section of the config) and any other JS file in the directory. However, if
    //the non-build bundle JS files will not be loaded after a build, you can
    //skip the optimization of those files, to speed up builds. Set this value
    //to true if you want to skip optimizing those other non-build bundle JS
    //files.
    skipDirOptimize: true,

    //Allow CSS optimizations. Allowed values:
    //- "standard": @import inlining and removal of comments, unnecessary
    //whitespace and line returns.
    //Removing line returns may have problems in IE, depending on the type
    //of CSS.
    //- "standard.keepLines": like "standard" but keeps line returns.
    //- "none": skip CSS optimizations.
    //- "standard.keepComments": keeps the file comments, but removes line
    //returns.  (r.js 1.0.8+)
    //- "standard.keepComments.keepLines": keeps the file comments and line
    //returns. (r.js 1.0.8+)
    //- "standard.keepWhitespace": like "standard" but keeps unnecessary whitespace.
    optimizeCss: "none",

    //Finds require() dependencies inside a require() or define call. By default
    //this value is false, because those resources should be considered dynamic/runtime
    //calls. However, for some optimization scenarios, it is desirable to
    //include them in the build.
    //Introduced in 1.0.3. Previous versions incorrectly found the nested calls
    //by default.
    findNestedDependencies: false,

    //If set to true, any files that were combined into a build bundle will be
    //removed from the output folder.
    removeCombined: false,

    //List the modules that will be optimized. All their immediate and deep
    //dependencies will be included in the module's file when the build is
    //done. If that module or any of its dependencies includes i18n bundles,
    //only the root bundles will be included unless the locale: section is set above.
    modules: [
        //Just specifying a module name means that module will be converted into
        //a built file that contains all of its dependencies. If that module or any
        //of its dependencies includes i18n bundles, they may not be included in the
        //built file unless the locale: section is set above.
        {
            name: "js/studio_lib",
            include: [
                "js/collections/asset",
                "js/collections/chapter",
                "js/collections/checklist",
                "js/collections/component_template",
                "js/collections/course_grader",
                "js/collections/course_update",
                "js/collections/group.js",
                "js/collections/group_configuration",
                "js/collections/metadata",
                "js/collections/textbook",
                "js/models/asset",
                "js/models/assignment_grade",
                "js/models/chapter",
                "js/models/checklist",
                "js/models/component_template",
                "js/models/course",
                "js/models/course_info",
                "js/models/course_update",
                "js/models/explicit_url",
                "js/models/group",
                "js/models/group_configuration",
                "js/models/location",
                "js/models/metadata",
                "js/models/module_info",
                "js/models/section",
                "js/models/settings/advanced",
                "js/models/settings/course_details",
                "js/models/settings/course_grader",
                "js/models/settings/course_grading_policy",
                "js/models/textbook",
                "js/models/uploads",
                "js/models/xblock_info",
                "js/models/xblock_outline_info",
                "js/sock",
                "js/utils/cancel_on_escape",
                "js/utils/change_on_enter",
                "js/utils/date_utils",
                "js/utils/drag_and_drop",
                "js/utils/handle_iframe_binding",
                "js/utils/modal",
                "js/utils/module",
                "js/utils/templates",
                "js/views/abstract_editor",
                "js/views/asset",
                "js/views/assets",
                "js/views/baseview",
                "js/views/checklist",
                "js/views/components/add_xblock",
                "js/views/components/add_xblock_button",
                "js/views/components/add_xblock_menu",
                "js/views/container",
                "js/views/course_info_edit",
                "js/views/course_info_handout",
                "js/views/course_info_helper",
                "js/views/course_info_update",
                "js/views/course_outline",
                "js/views/course_rerun",
                "js/views/edit_chapter",
                "js/views/edit_textbook",
                "js/views/feedback",
                "js/views/feedback_alert",
                "js/views/feedback_notification",
                "js/views/feedback_prompt",
                "js/views/group_configuration_details",
                "js/views/group_configuration_edit",
                "js/views/group_configuration_item",
                "js/views/group_configurations_list",
                "js/views/group_edit",
                "js/views/import",
                "js/views/list_textbooks",
                "js/views/metadata",
                "js/views/modals/base_modal",
                "js/views/modals/course_outline_modals",
                "js/views/modals/edit_xblock",
                "js/views/modals/validation_error_modal",
                "js/views/overview",
                "js/views/overview_assignment_grader",
                "js/views/pages/base_page",
                "js/views/pages/container",
                "js/views/pages/container_subviews",
                "js/views/pages/course_outline",
                "js/views/pages/group_configurations",
                "js/views/paging",
                "js/views/paging_footer",
                "js/views/paging_header",
                "js/views/settings/advanced",
                "js/views/settings/grader",
                "js/views/settings/grading",
                "js/views/settings/main",
                "js/views/show_textbook",
                "js/views/unit_outline",
                "js/views/uploads",
                "js/views/utils/create_course_utils",
                "js/views/utils/view_utils",
                "js/views/utils/xblock_utils",
                "js/views/validation",
                "js/views/video/transcripts/editor",
                "js/views/video/transcripts/file_uploader",
                "js/views/video/transcripts/message_manager",
                "js/views/video/transcripts/metadata_videolist",
                "js/views/video/transcripts/utils",
                "js/views/video/translations_editor",
                "js/views/xblock",
                "js/views/xblock_editor",
                "js/views/xblock_outline",
                "js/views/xblock_string_field_editor"
            ],
            create: true
        }
    ],

    //An alternative to "include". Normally only used in a requirejs.config()
    //call for a module used for mainConfigFile, since requirejs will read
    //"deps" during runtime to do the equivalent of require(deps) to kick
    //off some module loading.
    //deps: ["foo/bar/bee"],

    //Sets the logging level. It is a number. If you want "silent" running,
    //set logLevel to 4. From the logger.js file:
    //TRACE: 0,
    //INFO: 1,
    //WARN: 2,
    //ERROR: 3,
    //SILENT: 4
    //Default is 0.
    logLevel: 0,

    //Defines the loading time for modules. Depending on the complexity of the
    //dependencies and the size of the involved libraries, increasing the wait
    //interval may be required. Default is 7 seconds. Setting the value to 0
    //disables the waiting interval.
    waitSeconds: 60,

    //Introduced in 2.1.9: normally r.js inserts a semicolon at the end of a
    //file if there is not already one present, to avoid issues with
    //concatenated files and automatic semicolon insertion  (ASI) rules for
    //JavaScript. It is a very blunt fix that is safe to do, but if you want to
    //lint the build output, depending on the linter rules, it may not like it.
    //Setting this option to true skips this insertion. However, by doing this,
    //you take responsibility for making sure your concatenated code works with
    //JavaScript's ASI rules, and that you use a minifier that understands when
    //to insert semicolons to avoid ASI pitfalls.
    skipSemiColonInsertion: false,
})