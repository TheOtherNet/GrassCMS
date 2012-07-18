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
      @element.on 'mouseenter', (ev) ->
        this.style.border = '1px dotted grey'
      @element.on 'mouseleave', (ev) ->
        this.style.border = '0px'
      @element.on 'dragstart', @dragstart
      @element.on 'drag', @drag
      @element.on 'dragend', @dragend
      @element.on 'changed', @changed
      @element.on 'click', @toggleResize

    toggleResize: (ev) ->
      return if $(ev.target).data 'dragging'
      res=if $(this).data('resizing') == 1 then 0 else 1
      $(this).data('resizing', res)
      @enable_resizables if res == 1
      @disable_resizables if res == 0

    dragstart: (ev) ->
      $(this).data('dragging', true)
      $(this).data 'opacity', this.style.opacity
      this.style.border = '1px dotted grey'
      this.style.opacity = 0.4

    drag: (ev) ->
      $(this).attr 'draggable', 'true'
      this.style.top=ev.originalEvent.y + "px"
      this.style.left=ev.originalEvent.x + "px"
      this.style.position = "absolute"

    dragend: (ev) ->
      $(this).data('dragging', false)
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
