define(['js/models/course'], function(Course) {
    return function (courseInfo) {
        window.course = new Course(courseInfo);
    }
});
