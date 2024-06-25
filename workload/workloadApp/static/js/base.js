
canvasSprint.onclick = function(e) {
    var slice = planning_s.getElementAtEvent(e);
    if (!slice.length) return;

    var index = slice[0]._index;

    var urls = {{ urls_string|safe }};
    var url = urls[index];

    window.location.href = url;
}
