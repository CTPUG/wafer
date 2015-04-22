// Basic idea from Bojan Mihelac -
// http://source.mihelac.org/2010/02/19/django-time-widget-custom-time-shortcuts/

// Django imports jQuery into the admin site using noConflict(True)
// We wrap this in an anonymous function to stick to jQuery's $ idiom
// and ensure we're using the admin version of jQuery, rather than
// anything else pulled in

(function($) {
   var Schedule = {
      init: function() {
         time_format = get_format('TIME_INPUT_FORMATS')[0];
         $(".timelist").each(function(num) {
            // Clear existing list
            $( this ).empty();
            // Fill list with time values
            for (i=8; i < 20; i++) {
               var time = new Date(1970,1,1,i,0,0);
               quickElement("a", quickElement("li", this, ""),
                  time.strftime(time_format), "href",
                  "javascript:DateTimeShortcuts.handleClockQuicklink(" + num +
                  ", " + i + ");");
            }
         });
      }
   }

   // We need to be called after django's DateTimeShortcuts.init, which
   // is triggered by a load event
   $( window ).bind('load', Schedule.init);
}(django.jQuery));
