window.addEventListener('load', function() {
    let content = document.getElementById('content');
    let SubBar = document.getElementById('SubBar');

    let tempList = content.querySelectorAll('h1, h2, h3, h4, h5, h6');

    // For each header, create a button with a link in the SubBar
    tempList.forEach(function(header) {
        let button = document.createElement('button');
        button.innerText = header.innerText;
        button.addEventListener('click', function() {
            window.scrollTo(0, header.offsetTop);
        });
        SubBar.appendChild(button);

    });

    content = document.getElementById('MainBar');
    tempList = content.querySelectorAll('button');
    tempList[0].addEventListener('click', function() {
        // go to index.html
        window.location.href = "index.html";
    });
    tempList[1].addEventListener('click', function() {
        // go to index.html
        window.location.href = "building.html";
    });
    tempList[2].addEventListener('click', function() {
        // go to index.html
        window.location.href = "ship.html";
    });
    tempList[3].addEventListener('click', function() {
        // go to index.html
        window.location.href = "ressource.html";
    });
    tempList[4].addEventListener('click', function() {
        // go to index.html
        window.location.href = "research.html";
    });
    tempList[5].addEventListener('click', function() {
        // go to index.html
        window.location.href = "commands.html";
    });
});