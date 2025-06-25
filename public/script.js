const searchBox = document.querySelector("#searchBox");

searchBox.addEventListener("keydown", (evt) => {
    if (evt.key === "Enter"){
        event.preventDefault();
        let url = searchBox.value;
        
        fetch('/send-data', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: url})
        })
        .then(response => response.json())
        .then(data => {
            searchBox.value = '';
            if (data.result === 'exists'){
                window.location.href = `/productDetails?id=${data.ProductId}`;
            } else if (data.result === 'added'){
                window.location.href = '/NewRequest';
            }else{
                console.log("Some ERROR", data)
            }
        })
        .catch(err => console.log("Error", err))
    }
});


