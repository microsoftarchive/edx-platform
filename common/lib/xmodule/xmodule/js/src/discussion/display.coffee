class @InlineDiscussion extends XModule.Descriptor
  constructor: (element) ->
    @el = $(element).find('.discussion-module')
    @view = new DiscussionModuleView(el: @el)
    info = $('#discussion-author-more-info', element)
    info.hide()
    showInfo = (event) ->
        info.toggle()
        event.preventDefault()
    button = $(".discussion-more-info-button", element)
    button.click(showInfo)