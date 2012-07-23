#  Project: GrassCMS
#  Description: PersistentGrass plugin
#  Author: David Francos Cuartero <david@theothernet.co.uk>
#  License: GPL 2+

((jQuery, window) ->
  pluginName = 'PersistentGrass'
  document = window.document
  defaults =
    debug: false
    offset: 250

  class Plugin
    constructor: (@element, options) ->
      @options = $.extend {}, defaults, options
      @element = $ @element
      @_defaults = defaults
      @_name = pluginName
      @init()

    init: ->
      @do_resizable()
      @element.on 'mouseenter', @mouseenter
      @element.on 'mouseleave', @mouseleave
      @element.on 'dragstart', @dragstart
      @element.on 'drag', @drag
      @element.on 'dragend', @dragend
      @element.on 'click', @element_clicked
      @element.on 'changed', @changed
      @element.on 'contextmenu', @contextmenu
      @element.data 'offset', @options.offset
      $('#current_element_name').html("GrassCMS")

    element_clicked: (ev) ->
      foo = $($(this).children()[0]).attr('id')
      $('#panel_left').data('current_element', foo)
      if $(this).children('img').attr('src')
        source = $(this).children('img').attr('src').split('/')
        text = source[source.length - 1]
      else if $(this).children('div')
        text = "Text element"
      if ev.shiftKey
        $($(this).children()[0]).attr('contentEditable', 'true')
      $('#current_element_name').html(text)

    clear_all: ->
      $('#current_element_name').html("GrassCMS")

    mouseenter: ->
      this.style.border = '1px dotted grey'

    contextmenu: (ev) ->
        $('#menu').css 'top', ev.originalEvent.y - 35
        $('#menu').css 'left', ev.originalEvent.x - 300
        $('#menu').show()
        return false

    mouseleave: ->
      $($(this).children()[0]).attr('contentEditable', 'false')
      this.style.border = '0px'
      if $(this).css('height') != $(this).data('height')
        $(this).trigger 'changed', 'height', this.style.height
        $(this).data 'height', $(this).css('height')
      if $(this).css('width') != $(this).data('width')
        $(this).trigger 'changed', 'width', this.style.width
        $(this).data 'width', $(this).css('width')

    do_resizable: ->
      @element = @element.wrap('<div class="resizable">').parent()
      @element.data "width", @element.css('width')
      @element.data "height", @element.css('height')

    dragstart: (ev) ->
      $(this).trigger 'click'
      $(this).data 'opacity', this.style.opacity
      this.style.border = '1px dotted grey'
      this.style.opacity = 0.4

    drag: (ev) ->
      $(this).attr 'draggable', 'true'
      this.style.top=ev.originalEvent.y  + "px"
      if ev.originalEvent.x > $(this).data('offset')
        this.style.left=ev.originalEvent.x - $(this).data('offset') + "px"
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

($ document).ready ->
  ($ document).on 'click', (ev) ->
    if ev.button == 0 and ev.target.parentNode.id != "#menu"
      $('#menu').css("display", "none")

  ($ '#opacitypicker').on 'change', ->
    if $('#panel_left').data('current_element')
      $('#' + $('#panel_left').data('current_element')).css 'opacity', $('#opacitypicker').val()

  ($ '#colorpicker').on 'change', ->
    if $('#panel_left').data('current_element')
      $('#' + $('#panel_left').data('current_element')).css 'background', $('#colorpicker').val()
    else
      $('body').css 'background', $('#colorpicker').val()
