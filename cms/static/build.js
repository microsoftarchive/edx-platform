({
    mainConfigFile: 'require-config.js',
    paths: {
        "gettext": "empty:",
        "xmodule": "empty:",
        "mathjax": "empty:",
        "tender": "empty:",
        "youtube": "empty:"
    },
    waitSeconds: 60,
    skipDirOptimize: true,
    optimizeCss: "none",
    modules: [
        {name: 'js/require_pages/base'},
        {name: 'js/require_pages/index', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/login', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/outline', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/container', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/asset_index', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/checklists', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course_create_rerun', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course_info', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/edit_tabs', exclude: ["domReady", "domReady!", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/export', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/group_configurations', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/import', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/manage_users', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/register', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings_advanced', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings_graders', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/textbooks', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]}
    ]
})
