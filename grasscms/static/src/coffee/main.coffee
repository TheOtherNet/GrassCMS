#  Project: GrassCMS
#  Description: PersistentGrass plugin
#  Author: David Francos Cuartero <david@theothernet.co.uk>
#  License: GPL 2+

(($, window) ->
  pluginName = 'PersistentGrass'
  document = window.document
  defaults =
    debug: false

  class Plugin
    constructor: (@element, options) ->
      @options = $.extend {}, defaults, options
      @element = $ @element
      @_defaults = defaults
      @_name = pluginName
      @init()

    init: ->
      @do_resizable()
      @restore_from_server()
      @element.on 'mouseenter', (ev) ->
        this.style.border = '1px dotted grey'
      @element.on 'mouseleave', (ev) ->
        @mouseleave(this)
      @properties = [ "width", "height", 'opacity', 'top', 'left' ]
      @element.on 'dragstart', @dragstart
      @element.on 'drag', @drag
      @element.on 'dragend', @dragend
      @element.on 'changed', @changed

    mouseleave: (that) ->
      that.style.border = '0px'
      if that.css('height') != $(that).data('height')
        $(that).trigger 'changed', 'height', that.style.height
        $(that).data 'height', $(that).css('height')
      if that.css('width') != $(that).data('width')
        $(that).trigger 'changed', 'width', that.style.width
        $(that).data 'width', $(that).css('width')

    do_resizable: ->
      @element = @element.wrap('<div class="resizable">').parent()
      @element.data "width", @element.css('width')
      @element.data "height", @element.css('height')

    restore_from_server: ->
      @element.css(property, @get_property(property)) for property in @properties

    dragstart: (ev) ->
      $(this).data 'opacity', this.style.opacity
      this.style.border = '1px dotted grey'
      this.style.opacity = 0.4

    drag: (ev) ->
      $(this).attr 'draggable', 'true'
      this.style.top=ev.originalEvent.y + "px"
      this.style.left=ev.originalEvent.x + "px"
      this.style.position = "absolute"

    dragend: (ev) ->
      this.style.opacity = if $(this).data('opacity') > 0 then $(this).data('opacity') else 1
      $(this).trigger 'changed', 'top', ev.y
      $(this).trigger 'changed', 'left', ev.x

    changed: (attr, result) ->
      id = $(this).attr('id')
      $.ajax '/object/',
        type: 'PUT',
        dataType: 'json',
        data: JSON.stringify({
            'id': id,
            'attr': attr,
            'result': result
        })

  $.fn[pluginName] = (options) ->
    @each ->
      if !$.data(this, "plugin_#{pluginName}")
        $.data(@, "plugin_#{pluginName}", new Plugin(@, options))
)(jQuery, window)
