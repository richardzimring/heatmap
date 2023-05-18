// const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
// const { DynamoDBDocumentClient, GetCommand, PutCommand } = require("@aws-sdk/lib-dynamodb");
const express = require("express");
const serverless = require("serverless-http");
const app = express();

import { fetchExpirationDates } from "./requests/getDates";
import { fetchOptionData } from "./requests/getOptions";
import { fetchQuote } from "./requests/getQuote";
import { stringifyDates } from "./utils";

// const USERS_TABLE = process.env.USERS_TABLE;
// const client = new DynamoDBClient();
// const dynamoDbClient = DynamoDBDocumentClient.from(client);

app.use(express.json());

app.get("/data/:ticker", async function (req, res) {
  res.header("Access-Control-Allow-Origin", "*");

  const ticker = req.params.ticker;

  try {
    // get expiration dates
    const expirationDates = await fetchExpirationDates(ticker);
    const expirationDatesStringified = stringifyDates(expirationDates);

    // get general stock info data
    const quoteDataPromise = fetchQuote(ticker);
  
    // get options chains
    const optionDataPromise = fetchOptionData(ticker, expirationDates, expirationDatesStringified);

    // make requests concurrently
    const [stockData, optionData] = await Promise.all([quoteDataPromise, optionDataPromise])

    res.json({
      ...stockData,
      expirationDates,
      expirationDatesStringified,
      ...optionData
    });

  } catch (error) {
    console.log(error);
    res.status(400).json({ error: error.message });
  }
});

// app.get("/users/:userId", async function (req, res) {
//   const params = {
//     TableName: USERS_TABLE,
//     Key: {
//       userId: req.params.userId,
//     },
//   };

//   try {
//     const { Item } = await dynamoDbClient.send(new GetCommand(params));
//     if (Item) {
//       const { userId, name } = Item;
//       res.json({ userId, name });
//     } else {
//       res
//         .status(404)
//         .json({ error: 'Could not find user with provided "userId"' });
//     }
//   } catch (error) {
//     console.log(error);
//     res.status(500).json({ error: "Could not retreive user" });
//   }
// });

// app.post("/users", async function (req, res) {
//   const { userId, name } = req.body;
//   if (typeof userId !== "string") {
//     res.status(400).json({ error: '"userId" must be a string' });
//   } else if (typeof name !== "string") {
//     res.status(400).json({ error: '"name" must be a string' });
//   }

//   const params = {
//     TableName: USERS_TABLE,
//     Item: {
//       userId: userId,
//       name: name,
//     },
//   };

//   try {
//     await dynamoDbClient.send(new PutCommand(params));
//     res.json({ userId, name });
//   } catch (error) {
//     console.log(error);
//     res.status(500).json({ error: "Could not create user" });
//   }
// });

app.use((req, res, next) => {
  return res.status(404).json({
    error: "Not Found",
  });
});


module.exports.handler = serverless(app);