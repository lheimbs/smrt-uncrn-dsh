function get_selection_ids() {
    return $(".dataTable").DataTable().rows( { selected: true }).data().toArray().map(element => element.id);
}