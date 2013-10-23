// Basic idea from Bojan Mihelac -
// http://source.mihelac.org/2010/02/19/django-time-widget-custom-time-shortcuts/

var Schedule = {
   init: function() {
      time_format = get_format('TIME_INPUT_FORMATS')[0];
      django.jQuery(".timelist").each(function(num) {
         // Clear existing list
         django.jQuery( this ).empty();
         // Fill list with time values
         for (i=8; i < 20; i++) {
            var time = new Date(1970,1,1,i,0,0);
            quickElement("a", quickElement("li", this, ""),
               time.strftime(time_format), "href",
               "javascript:DateTimeShortcuts.handleClockQuicklink(" + num +
               ", '" + time.strftime(time_format) + "');");
         }
      });
   }
}

addEvent( window, 'load', Schedule.init);
