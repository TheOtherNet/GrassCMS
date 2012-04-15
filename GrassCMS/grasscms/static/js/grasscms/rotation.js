var rotating=false;

function mouse(evt, img) { img=$(img);
    if (evt.shiftKey && window.stoped != true){      
        var offset = img.offset(); console.debug(evt.target);        
        var center_x = (offset.left) + (img.width() / 2);
        var center_y = (offset.top) + (img.height() / 2);
        var mouse_x = evt.pageX;
        var mouse_y = evt.pageY;
        var radians = Math.atan2(mouse_x - center_x, mouse_y - center_y);
        var degree = (radians * (180 / Math.PI) * -1) + 90;

        img.css('-moz-transform', 'rotate(' + degree + 'deg)');
        img.css('-webkit-transform', 'rotate(' + degree + 'deg)');
        img.css('-o-transform', 'rotate(' + degree + 'deg)');
        img.css('-ms-transform', 'rotate(' + degree + 'deg)');
        $.ajax({ url: "/set_rotation/img/" + img.attr('id').replace('img','') + "/" + degree })  // TODO: This only supports images =(

    }
}


