/*
    GrassCMS - CMS for the mases
    Copyright (C) 2012 GrassCMS team

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

    GrassCMS javascript functions.
*/
function get_o(elem){ 
    console.debug($(this).parent().parent().parent().parent().data('type'));
    return $(elem).parent().parent().parent().parent().children($(this).parent().parent().parent().parent().data('type'))
}
function strStartsWith(str, prefix) {
    return str.indexOf(prefix) === 0;
}
function delete_(element){
    if ( strStartsWith($(element).attr('id'), 'mep') ){ id_=$(element).parent().attr('id').replace($(element).data('type'),'').replace('video',''); } else {id_=$(element).attr('id').replace(element.data('type'), '').replace('menu','');}
    if (!element.data('type')){ element.data('type', element.parent().data('type')); }
    $.ajax({ 
            url: '/delete_' + $(element).data('type').replace('.','') +'/' + id_ + "/", 
            type: "DELETE", method:"DELETE", 
            complete: function(data){ 
                console.debug($(element).data('type') + id_);
                $("#"+$(element).data('type') + id_).parent().hide(); 
            } 
        }); 
}
