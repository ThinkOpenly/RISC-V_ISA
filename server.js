const cors = require("cors");
const express = require("express");
const parser = require("body-parser");
const app = express();
const https = require("https");
app.use(cors({ credentials: true, origin: true }));
app.use(express.static(`./build`));

app.use(parser.json({ limit: "50mb" }));

app.use(parser.urlencoded({ extended: false }));

// Set the headers that will be returned by this application.
// "Access-Control-Allow-Origin", "*" is needed for SAM UI to avoid CORS error
app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header(
        "Access-Control-Allow-Headers",
        "authorization, cache-control, X-Requested-With, Content-Type, Accept"
    );
    res.header(
        "Access-Control-Allow-Methods",
        "POST, GET, PUT, DELETE, OPTIONS"
    );

    if ("OPTIONS" == req.method) {
        res.sendStatus(200);
    } else {
        next();
    }
});

app.options("*", function(req, res, next) {
    res.header("Access-Control-Allow-Origin", req.get("Origin") || "*");
    res.header(
        "Access-Control-Allow-Headers",
        "Authorization,Origin, X-Requested-With, Content-Type, Accept"
    );
    res.header(
        "Access-Control-Allow-Methods",
        "POST, GET, PUT, DELETE, OPTIONS"
    );

    res.sendStatus(200);
});

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

app.get("*", function(request, response) {
    response.sendFile("index.html", { root: "./build/" });
});

////////////////////////////////////////////////////////////////////////////////

function main() {
    var port = process.env.PORT || port;
    app.listen(port);

    console.log("server: running local environmnet on http://localhost:3000");
}

main();
