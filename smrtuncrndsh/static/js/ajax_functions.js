function handleAjaxError(response, textStatus, errorThrown) {
    console.debug("ajax setup, error");
    console.debug(response, textStatus, errorThrown);
    // Handle AJAX errors
    if (response.status==0) {
        makeFlashMessage('error', 'You are offline! Please Check Your Network.');
    } else if(response.status==404) {
        makeFlashMessage('error', 'Requested URL not found.');
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