var $ = (jQuery)

$(document).ready(function() {

    function formatTalkCategorizationResult(item) {
        var parts = item.text.split(/:\s*/)
        var name = parts[0]
        var description = parts[1]
        return $([
            "<div>",
            "<div>",
            "<strong>",
            name,
            "</strong>",
            "</div>",
            description,
            "</div>"
        ].join(""))
    }

    function formatTalkCategorizationSelection(item) {
        return item.text.split(/:\s*/)[0]
    }

    $('.talk-categorization').select2({
        templateResult: formatTalkCategorizationResult,
        templateSelection: formatTalkCategorizationSelection,
        dropdownAutoWidth: true
    })
})
