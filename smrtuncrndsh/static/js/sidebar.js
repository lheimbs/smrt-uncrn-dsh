
function sidebar_open() {
    document.getElementById("main").classList.remove('sidebar-closed');
    document.getElementById("page_sidebar").classList.remove('sidebar-closed');
    document.getElementById("open_sidebar").classList.remove('sidebar-closed');
    document.getElementById("main").classList.add('sidebar-open');
    document.getElementById("page_sidebar").classList.add('sidebar-open');
    document.getElementById("open_sidebar").classList.add('sidebar-open');
    // document.getElementById("main").style.marginLeft = "85px";
    // document.getElementById("page_sidebar").style.width = "85px";
    // document.getElementById("page_sidebar").style.display = "block";
    // document.getElementById("open_sidebar").style.display = 'none';
}


function sidebar_close() {
    document.getElementById("main").classList.remove('sidebar-open');
    document.getElementById("page_sidebar").classList.remove('sidebar-open');
    document.getElementById("open_sidebar").classList.remove('sidebar-open');
    document.getElementById("main").classList.add('sidebar-closed');
    document.getElementById("page_sidebar").classList.add('sidebar-closed');
    document.getElementById("open_sidebar").classList.add('sidebar-closed');
    // document.getElementById("main").style.marginLeft = "0%";
    // document.getElementById("page_sidebar").style.display = "none";
    // document.getElementById("open_sidebar").style.display = "inline-block";
}
