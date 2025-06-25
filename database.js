const { response, query } = require('express');
const {createPool} = require('mysql2');
require('dotenv').config();

const db = createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
})

async function addRequest(link){
    let query = 'insert into new_requests values(?);'
    try{
        await new Promise((resolve, reject) => {
            db.query(query, [link], (err, res) =>{
                if (res) {
                    resolve(res);
                }
                if (err){
                    reject(err);
                }
            })
        });
        return true;
    }
    catch(err){
        console.log(`Error in adding ${link} to requests`);
        return false;
    }
}

async function getAllProductLinks() {
    let product_links = new Set();
    let query = 'SELECT product_link FROM products;';

    try {
        const res = await new Promise((resolve, reject) => {
            db.query(query, (err, results) => {
                if (err) reject(err);
                else resolve(results);
            });
        });

        for (const obj of res) {
            product_links.add(obj.product_link);
        }

    } catch (err) {
        console.log("Error in getting product links:", err);
    }

    return product_links; // Will be the Set of product links or an empty Set in case of an error
}

async function getId(url) {
    const query = "SELECT product_id FROM products WHERE product_link = ?";

    return new Promise((resolve, reject) => {
        db.query(query, [url], (err, res) => {
            if (err) {
                console.error("Error in getting id of link " + url, err);
                return reject(new Error("Database query failed")); // Reject the promise with an error
            }
            if (res && res.length > 0) {
                resolve(res[0].product_id); // Resolve the promise with the product_id
            } else {
                resolve(null); // Resolve with null if no result found
            }
        });
    });
}

async function getLatestPrice(id){
    const query = `SELECT price FROM product_prices WHERE product_id = ? ORDER BY date DESC LIMIT 1;`;
    return new Promise((resolve, reject) =>{
        db.query(query, [id], (err, res)=>{
            if (err) reject(err);
            if (res) resolve(res[0]);
        })
    })
}

async function getSpecification(id){
    const query = `select spec_key, spec_value from product_specifications where product_id = ?;`;
    return new Promise((resolve, reject) =>{
        db.query(query, [id], (err, res)=>{
            if (err) reject(err);
            if (res) resolve(res);
        })
    })
}

async function getNameImg(id){
    const query = `select product_name, img from products where product_id = ?;`;
    return new Promise((resolve, reject) =>{
        db.query(query, [id], (err, res) => {
            if (err) reject(err);
            if (res) resolve(res[0]);
        })
    })
}

async function getDetails(id){
    try{
        const rawDetails = await Promise.all([getNameImg(id), getLatestPrice(id), getSpecification(id), getMinMaxPrice(id)]);
        const processedDetails = {
            name: rawDetails[0].product_name,
            img: rawDetails[0].img,
            price: rawDetails[1].price,
            specifications: rawDetails[2],
            minPrice: rawDetails[3].minPrice,
            maxPrice: rawDetails[3].maxPrice
        }
        return processedDetails;
    } catch(err){
        console.log("ERROR IN FETCHING DETAILS PRODUCT ID = "+ id, err);
        return -1;
    }
}


async function getTrackedPrices(id){
    const query = 'select date, price from product_prices where product_id = ?;';
    return new Promise((resolve, reject) =>{
        db.query(query, [id], (err, res)=>{
            if (err) reject(err)
            if (res) resolve(res)
        })
    })
}

async function isUniqueAlert(id, email){
    const query = 'select product_id, email from notifications;';
    return new Promise((resolve, reject) =>{
        db.query(query, (err, res)=>{
            if (err) reject(err)
            if (res) {
                for (alert of res){
                    if(alert.product_id === id && alert.email === email){
                        resolve(false)
                    }
                }
                resolve(true)
            }
        })
    })
}


async function addNotification(id, email, price){
    const unique = await isUniqueAlert(Number(id), email);
    if (unique) {
        const query = 'insert into notifications values(?, ?, ?);';
        return new Promise((resolve, reject) =>{
            db.query(query, [id, email, price], (err,res) =>{
                if (err) reject(err)
                if (res) resolve(res)
            })
        })
    } else{
        const query = 'update notifications set price=? where product_id=? and email=?;';
        return new Promise((resolve, reject)=>{
            db.query(query, [price, id, email], (err, res)=>{
                if (err) reject(err)
                if (res) resolve(res)

            })
        })
    }  
}

async function getMinMaxPrice(id){
    return new Promise((resolve, reject)=>{
        const query = `select min(price) as minPrice, max(price) as maxPrice from product_prices where product_id=?;`;
        db.query(query, [id], (err, res)=>{
            if (err) reject(err)
            if (res) resolve(res[0])
        })
    })
    
}

module.exports.addRequest = addRequest;
module.exports.getAllProductLinks = getAllProductLinks;
module.exports.getId = getId;
module.exports.getDetails = getDetails;
module.exports.getTrackedPrices = getTrackedPrices;
module.exports.addNotification = addNotification;