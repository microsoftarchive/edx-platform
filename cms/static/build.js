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
        {name: 'js/pages/deps'},
        {name: 'js/pages/base', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/index', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/course', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/login', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/outline', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/container', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/asset_index', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/checklists', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/course_create_rerun', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/course_info', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/edit_tabs', exclude: ["domReady", "domReady!", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/export', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/group_configurations', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/import', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/manage_users', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/register', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/settings', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/settings_advanced', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/settings_graders', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]},
        {name: 'js/pages/textbooks', exclude: ["domReady", "domReady!", "backbone", "jquery", "underscore"]}
    ]
})
