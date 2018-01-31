var config = require('./config');
var url=require('url');
//path=url.parse("coap://localhost/time");
path="@coap://localhost/time";
console.log(path.split('@')[1]);