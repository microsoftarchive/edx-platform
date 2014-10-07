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
        {name: 'js/require_pages/index', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/login', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/outline', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/container', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/asset_index', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/checklists', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course_create_rerun', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/course_info', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/edit_tabs', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/export', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/group_configurations', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/import', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/manage_users', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/register', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings_advanced', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/settings_graders', exclude: ["backbone", "jquery", "underscore"]},
        {name: 'js/require_pages/textbooks', exclude: ["backbone", "jquery", "underscore"]}
    ]
})
