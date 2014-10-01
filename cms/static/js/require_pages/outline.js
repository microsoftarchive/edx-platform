define(['domReady!', 'jquery',
    "js/views/pages/course_outline", "js/models/xblock_outline_info"
], function(dom, $, CourseOutlinePage, XBlockOutlineInfo) {
    return function (XBlockOutlineInfoJSON, initialStateJSON) {
        var courseXBlock = new XBlockOutlineInfo(XBlockOutlineInfoJSON, { parse: true });
        var view = new CourseOutlinePage({
            el: $('#content'),
            model: courseXBlock,
            initialState: initialStateJSON
        });
        view.render();
    };
});
