jQuery.fn.extend({

    persistentdata: function(what, value){
        $(this).trigger('cssModified', [what, 'in_post', value]);
    },

    persistentcss: function(what, value){
        $(this).css(what, value);
        $(this).trigger('cssModified', [what, value]);
    },

    persistent: function(type){
    /*
        Make an object transparently persistent in size and position.
        This also interacts with the server to make css properties also persistent when you use $(foo).persistencss() call instead of $(foo).css().
        @param type: Type, how to identify this kind of object in the server 
    */

    function set_data(id, what, value, data){
        $.ajax({ type: 'POST', url: "/set/" + what + "/" + id + "/" + value, data:{ 'result': data } }); 
    }

    function remote_properties(element, what){ set_data(element.data('id'), what, element.css(what)); }

    function get_data(element, what, properties, transform){
        if (!transform){ transform="elem";}
        $.ajax({ url: "/get/" + what + "/" + element.attr('id'), method:"POST", type:"POST",
            success: function(data){ 
                $(properties).each(function(){ 
                    element.children('.img').css('top', "auto").css('left', 'auto');
                    element.css(this +"", transform.replace('elem', data));
                });
            }
        }); 
    }

    function set_dimensions(type, id, ui){ 
        set_data(id, 'width', ui.size.width);
        set_data(id, 'height', ui.size.height);
    }

    function set_position(type, id, ui){ 
        set_data(id, 'x', ui.position.top);
        set_data(id, 'y', ui.position.left);
    }

    return this.each(function(){ var element=$(this); 
        element.bind('cssModified', function(event, what, value, data) { 
            set_data($(event.currentTarget).attr('id'), what, value, data);
        });

        if (element.children(type).length > 0){ var id = get/number(element.children(type).attr('id'))}
        else { var id = get_number(element.attr('id')) }

        if (element.parent().attr('id') != "filedrag" ){ element=element.parent();}

        element.resizable({ 
            alsoResize: $.merge(element.children('.wysihtml5-sandbox'), element.children('.alsoResizable')), 
            stop: function(ev, ui){ 
                set_dimensions(type, id, ui); }} 
        ).draggable({ 
            stop: function(ev, ui){ 
                set_position(type, id, ui); }} 
        ); 

        element.append($('#standard_tools_model').html());
        console.debug(element);
        get_data(element, 'zindex', Array('opacity'));
        get_data(element, 'opacity', Array('opacity'));
        get_data(element, 'rotation', Array('-moz-transform', '-webkit-transform', '-o-transform', '-ms-transform'), 'rotate(elem)');
        get_data(element, 'x', Array('top'), 'elempx');
        get_data(element, 'y', Array('left'), 'elempx');
    });
}});
