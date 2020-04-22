// Override the default setting on the django admin DateTimeShortcut
// Django 2 nicely does make this overridable, but we need to
// set it up before the DateTimeShortcuts init is called by
// window.onload, so we attach it to DOMContentLoaded
//
// The names of the input fields are also a bit opaque, and
// unfornately not something we can easily pass in

document.addEventListener("DOMContentLoaded", function() {
   // These are for the single admin pages
   window.DateTimeShortcuts.clockHours.end_time_1 = [];
   window.DateTimeShortcuts.clockHours.start_time_1 = [];
   for (let hour = 8; hour <= 20; hour++) {
       let verbose_name = new Date(1970, 1, 1, hour, 0, 0).strftime('%H:%M');
       window.DateTimeShortcuts.clockHours.end_time_1.push([verbose_name, hour])
       window.DateTimeShortcuts.clockHours.start_time_1.push([verbose_name, hour])
   }
   // This is for the inline options - we define 30, which is hopefully sane
   for (let inline = 0; inline < 30; inline++) {
      let name = 'form-' + inline + '-end_time_1';
      window.DateTimeShortcuts.clockHours[name] = [];
      for (let hour = 8; hour <= 20; hour++) {
          let verbose_name = new Date(1970, 1, 1, hour, 0, 0).strftime('%H:%M');
          window.DateTimeShortcuts.clockHours[name].push([verbose_name, hour])
      }
   }
});
