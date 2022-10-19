// Hide users table on license status page by deafult
// var elements = document.querySelectorAll(".users");
// elements.forEach(element => {
//     element.style.display = "none";
// })

// Toggle button for users table visibility
$('.feature').click(function () {
    var next = $(this).next()
    if (next.hasClass("users")) {
        next.toggle()
    }
})


// Show/hide advanced search field
$('#advanced-search-button').click(function () {
    $('#advanced-search-field').toggleClass("hide-field")
});


// Clickable path cell in general_literature.html
$('.path-cell').click(function () {
    $(this).toggleClass("show-path")
});