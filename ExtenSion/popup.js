const btn=document.getElementById("analysis");
btn.addEventListener("click",function() {
    btn.disabled=true;
    btn.innerHTML="Analyzing...";
    chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
// we are just quering the active tab that is we are fetching the youtube url from the current tab the provide the api to fetch vedio id
        var url=tabs[0].url; // tabs[0] is active tab
        //when url is entered an http request is sent to the server and further gets the data from the server and displays it to you
        var xhr=new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:5000/final?url=" + url, true);
        xhr.onload = function() {
            var response = JSON.parse(xhr.responseText);
            // Process the response JSON object
            // Example: Accessing the 'neg' and 'pos' variables
            var neg = response.neg;
            var pos = response.pos;
            document.getElementById("negt").innerHTML = `NEGATIVE REVIEWS = ${neg} `;
            document.getElementById("post").innerHTML = `POSITIVE REVIEWS = ${pos}`;
            btn.disabled=false;
            btn.innerHTML="Analyze";
        }
        xhr.send();
    }); 

});
