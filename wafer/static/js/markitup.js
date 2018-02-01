'use strict'
$('.django-markitup-config').each(function(index) {
  var element = $(this.getAttribute('data-element'));
  var preview_url = this.getAttribute('data-preview-url');
  var auto_preview = this.getAttribute('data-auto-preview') == '1';
  if (!element.hasClass("markItUpEditor")) {
    if (preview_url) {
      mySettings["previewParserPath"] = preview_url;
    }
    element.markItUp(mySettings);
  }
  if (auto_preview) {
    $('a[title="Preview"]').trigger('mouseup');
  }
});
