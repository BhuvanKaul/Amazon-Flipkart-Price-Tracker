document.addEventListener("DOMContentLoaded", async ()=>{
    const urlParams = new URLSearchParams(window.location.search);
    const queryId = urlParams.get('id');

    if (queryId){
        const response = await fetch(`/get-product-details?id=${queryId}`);
        const details = await response.json();

        const name = document.querySelector('#product_name');
        const price = document.querySelector('#product_price');
        const min_price = document.querySelector('#min_price');
        const max_price = document.querySelector('#max_price');
        const img = document.querySelector('.product_img');
        const specsTableBody = document.querySelector('#specifications tbody');

        name.innerText = details.name;
        price.innerText = 'Current Price: ₹ ' + details.price;
        min_price.innerText = 'Minimum Recorded Price: ₹ ' + details.minPrice;
        max_price.innerText = 'Maximum Recorded Price: ₹ ' + details.maxPrice;
        img.src = details.img;

        let specsRows = '';
        for (let obj of details.specifications) {
            specsRows += `<tr><td>${obj.spec_key}</td><td>${obj.spec_value}</td></tr>`;
        }
        specsTableBody.innerHTML = specsRows;


        const price_response = await fetch(`/get-tracked-prices?id=${queryId}`);
        const price_details = await price_response.json();
        
        const labels = price_details.map(data => new Date(data.date).toLocaleDateString());
        const prices = price_details.map(data => parseFloat(data.price));

        const ctx = document.getElementById('price_chart').getContext('2d');
        const priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: prices,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price (INR)'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
        


    }else{
        console.log("No ID Given");
    }
})


document.addEventListener("DOMContentLoaded", () => {
    const notifyButton = document.querySelector("#notification_button");
    const popUp = document.getElementById("popUp");
    const closeButton = popUp.querySelector(".close");
    const submitButton = popUp.querySelector("#submit_notification");

    notifyButton.addEventListener("click", () => {
        popUp.style.display = 'block';
    });

    closeButton.addEventListener("click", () => {
        popUp.style.display = 'none';
    });

    window.addEventListener("click", (event) => {
        if (event.target === popUp) {
            popUp.style.display = 'none';
        }
    });

    submitButton.addEventListener("click", () => {
        const urlParams = new URLSearchParams(window.location.search);
        const queryId = urlParams.get('id');

        const emailInput = document.getElementById("email");
        const alertPriceInput = document.getElementById("alert_price");
        const email = emailInput.value;
        const alertPrice = alertPriceInput.value;

        if (email && alertPrice) {
            console.log(1);
            const successBanner = document.getElementById("successBanner");
            successBanner.classList.add('show');

            popUp.style.display = "none";
            emailInput.value = '';
            alertPriceInput.value = '';

            fetch('/send-notification-request', {
                method: 'post',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({productId: queryId, email: email, alertPrice: alertPrice})
            })

            setTimeout(() => {
                successBanner.classList.remove('show');
            }, 4000);

        } else {
            if (!email){
                emailInput.style.borderColor = 'red';
                emailInput.classList.add('shake');
            }
            if(!alertPrice){
                alertPriceInput.style.borderColor = 'red';
                alertPriceInput.classList.add('shake');          
            }

            setTimeout(()=>{
                emailInput.classList.remove('shake');
                alertPriceInput.classList.remove('shake');
                emailInput.style.borderColor = '#ddd';
                alertPriceInput.style.borderColor = '#ddd';
            },300);
        }
    });
});

