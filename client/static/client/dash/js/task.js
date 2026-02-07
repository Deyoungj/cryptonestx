
var btc = document.getElementById("Bitcoin_price")
var eth = document.getElementById("Ethereum_price")
var lte = document.getElementById("Litecoin_price")
var dash = document.getElementById("DASH_price")


var liveprices = {
    "async": true,
    "scroosDomain":true,
    "url":"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Clitecoin%2Cethereum%2Cdash&vs_currencies=usd&include_24hr_change=true",
    "method":"GET",
    "headers":{}
}


$.ajax(liveprices).done(function(response){
    console.log(response);

    btc.innerHTML = '$'+`${response.bitcoin.usd} <span>+${response.bitcoin.usd_24h_change.toFixed(2)}%</span>`
    eth.innerHTML = '$'+`${response.ethereum.usd} <span>+${response.ethereum.usd_24h_change.toFixed(2)}%</span>`
    lte.innerHTML = '$'+`${response.litecoin.usd} <span>+${response.litecoin.usd_24h_change.toFixed(2)}%</span>`
    dash.innerHTML = '$'+`${response.dash.usd} <span>+${response.dash.usd_24h_change.toFixed(2)}%</span>`

})