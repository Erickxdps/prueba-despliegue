function searchTable(containerId) {
    var input, filter, container, items, itemContent, i, j, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    container = document.getElementById(containerId);
    
    if (container.tagName === 'TABLE') {
        items = container.getElementsByTagName("tr");
        for (i = 1; i < items.length; i++) {
            items[i].style.display = "none";
            itemContent = items[i].getElementsByTagName("td");
            for (j = 0; j < itemContent.length; j++) {
                if (itemContent[j]) {
                    txtValue = itemContent[j].textContent || itemContent[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        items[i].style.display = "";
                        break;
                    }
                }
            }
        }
    } else {
        items = container.getElementsByClassName("column");
        for (i = 0; i < items.length; i++) {
            itemContent = items[i].getElementsByClassName("content")[0];
            if (itemContent) {
                txtValue = itemContent.textContent || itemContent.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    items[i].style.display = "";
                } else {
                    items[i].style.display = "none";
                }
            }
        }
    }
}