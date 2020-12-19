function handleAjaxError(response, textStatus, errorThrown) {
    console.debug("ajax setup, error");
    console.debug(response, textStatus, errorThrown);
    // Handle AJAX errors
    if (response.status==0) {
        makeFlashMessage('error', 'You are offline! Please Check Your Network.');
    } else if(response.status==400) {
        makeFlashMessage('error', 'Sheit, I think you need to reload this... or it is broken >.<');
    } else if(response.status==401) {
        makeFlashMessage('error', "Fuck, you sadly don't have access to this :'(");
    } else if(response.status==402) {
        makeFlashMessage('error', errorThrown);
    } else if(response.status==403) {
        makeFlashMessage('error', "Bummer, it seems like your don't have access to this page :(");
    } else if(response.status==404) {
        makeFlashMessage('error', "Damn, this page or w/e does not seem to exist :/");
    } else if(response.status==500) {
        makeFlashMessage('error', 'Internal Server Error.');
    } else if(textStatus=='parsererror') {
        makeFlashMessage('error', 'Parsing JSON Request failed.');
    } else if(textStatus=='timeout'){
        makeFlashMessage('error', 'Request Time out.');
    } else if(response.responseJSON=="The CSRF token has expired."){
        makeFlashMessage('error', "The CSRF token has expired. Please refresh the page.");
    } else {
        makeFlashMessage('error', 'Unknow Error: '+errorThrown);
    }
}