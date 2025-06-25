const db = require('./database.js');
const express = require('express');
const path = require('path');

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public'));

function clipUrl(url) {
    if (url.includes('www.amazon.in')){
        const dpIndex = url.indexOf("/dp/");
        if (dpIndex !== -1) {
            const endIndex = url.indexOf("/", dpIndex + 4);
            const clippedUrl = endIndex !== -1 ? url.slice(0, endIndex) : url;
            return clippedUrl;
        }
    }
    else if (url.includes('www.flipkart.com')){
        const pIdIndex = url.indexOf("?pid=");
        if (pIdIndex !== -1){
            const endIndex = url.indexOf("&", pIdIndex + 5);
            const clippedUrl = endIndex !== -1 ? url.slice(0, endIndex) : url
            return clippedUrl
        }
    }
    return url;
}

app.post('/send-data', async (req,res) =>{
    const rawUrl = req.body.url;
    const url = clipUrl(rawUrl)
    console.log("recieved to backend(server.js): "+ url);

    try{
        const trackingProducts = await db.getAllProductLinks();
        if (trackingProducts.has(url)){
            let id;
            try{
                id = await db.getId(url);
            } catch(err){
                console.log("Error in getting ID of product")
            }
            res.send({result:"exists", ProductId:id});
        }
        else{
            const addedToDB = await db.addRequest(url);
            if (addedToDB){
                res.send({result:"added", ProductId:null})
                console.log("success added to DB: "+ url);
            }
            else{
                res.send({result:"added", ProductId:null})
                console.log("Request already accepted: "+url);
            }

        }
    }
    catch(err){
        console.log("ERROR IN GETTING PRODUCTS", err)
    }   
})

app.get('/get-product-details', async (req, res)=>{
    const productId = req.query.id;

    try{
        const productDetails = await db.getDetails(productId);
        res.json(productDetails);
    }catch(err){
        console.log("Error in getting Details in backend server.js for id: "+ productId, err);
        res.send("There is some error");
    }
})

app.get('/get-tracked-prices', async(req, res)=>{
    const productId = req.query.id;

    try{
        const pricesList = await db.getTrackedPrices(productId);
        res.json(pricesList);
    } catch(err){
        console.log("ERROR IN GETTING PRICES IN BACKEND SERVER.JS FOR PRODUCT ID: "+ productId, err);
        res.send("There is some Error");
    }
})


app.post('/send-notification-request', async(req, res)=>{
    const productId = req.body.productId;
    const email = req.body.email;
    const alertPrice = req.body.alertPrice;

    try {
        await db.addNotification(productId, email, alertPrice);
        res.send("Success");
    } catch(err){
        console.log(`Error in adding notification: (${productId}, ${email}, ${alertPrice})`)
        console.log(err);
        res.send("Error")
    }
})


app.get('/productDetails', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'productDetails.html'));
});

app.get('/NewRequest', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'NewRequest.html'));
});


app.listen(port, ()=> {
    console.log(`Server is running on http://localhost:${port}`);
})