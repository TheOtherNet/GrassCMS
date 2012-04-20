// TODO Make this jquery xD
function makeGuideY(dom_element) {
    $(dom_element).draggable({
        axis: "y",
        containment: "#filedrag",
        drag: function() {
            var position = $(this).position();
            var yPos = $(this).css('top');
            $(this).find($('.pos')).text('Y: ' + yPos);
        },
        start: function() {
            $(this).find($('.pos')).css('display', 'block');
        },
        stop: function() {
            $(this).find($('.pos')).css('display', 'none');

            if ($(this).hasClass("draggable-y-newest")) {
                $(this).removeClass("draggable-y-newest");
                $("#filedrag .y-guide").clone().removeClass("y-guide").addClass("draggable-y-newest").appendTo("#filedrag").each(function() {
                    makeGuideY(this);
                });
            }
        }
    });
}

function makeGuideX(dom_element) {
    $(dom_element).draggable({
        axis: "x",
        containment: "#filedrag",
        drag: function() {
            var position = $(this).position();
            var xPos = $(this).css('left');
            $(this).find($('.pos')).text('X: ' + xPos);
        },
        start: function() {
            $(this).find($('.pos')).css('display', 'block');
        },
        stop: function() {
            $(this).find($('.pos')).css('display', 'none');

            if ($(this).hasClass("draggable-x-newest")) {
                $(this).removeClass("draggable-x-newest");
                $("#filedrag .x-guide").clone().removeClass("x-guide").addClass("draggable-x-newest").appendTo("#filedrag").each(function() {
                    makeGuideX(this);
                });
            }
        }
    });
}
