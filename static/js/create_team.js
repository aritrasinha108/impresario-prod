(function () {
    var options = [];
    for (i = 0; i < ids.length; i++) {
        var option = "";
        if (admin[i] == 1)
            option =
                "<input type=checkbox checked onclick='event.preventDefault()' value=" +
                ids[i] +
                " id=" +
                ids[i] +
                " name=checks>" +
                names[i] +
                "</input>";
        else
            option =
                "<input type=checkbox checked value=" +
                ids[i] +
                " id=" +
                ids[i] +
                " name=checks >" +
                names[i] +
                "</input>";   
            options.push(option);
    }
    document.querySelector("#team-members").innerHTML = options.join("<br>");
}) ();
  