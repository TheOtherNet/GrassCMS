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

function assign_menu(blog_id){ 
    /*
        Assign / Update a menu to a blog.
        After successful creation, it reloads the page.
    */
    $.ajax({
        url:'/update_menu/' + blog_id +'/', 
        type : 'POST', 
        success: function(data_){
            location.reload(true);
        } 
    }); 
}
 
function unassign_menu(blog_id){ 
    /*
        Delete a menu
        After successful creation, it reloads the page.
    */
    $.ajax({
        url:'/delete_menu/' + blog_id +'/', 
        type : 'POST', 
        success: function(data_){
            location.reload(true);
        } 
    }); 
}