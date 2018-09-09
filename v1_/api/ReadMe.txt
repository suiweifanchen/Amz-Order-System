

数据库结构
+------------------------------+--------------+------+-----+---------------------+-----------------------------+
| Field                        | Type         | Null | Key | Default             | Comment                     |
+------------------------------+--------------+------+-----+---------------------+-----------------------------+
| AmazonOrderId                | varchar(50)  | NO   | PRI | NULL                |                             |
| LastUpdateDate               | timestamp    | NO   | PRI | 0000-00-00 00:00:00 |                             |
| ASIN                         | varchar(50)  | NO   | PRI | NULL                |                             |
| SellerSKU                    | varchar(50)  | YES  |     | NULL                |                             |
| PaidDate                     | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| LatestShipDate               | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| OrderType                    | varchar(50)  | YES  |     | NULL                |                             |
| PurchaseDate                 | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| BuyerEmail                   | varchar(100) | YES  |     | NULL                |                             |
| IsReplacementOrder           | varchar(10)  | YES  |     | NULL                |                             |
| NumberOfItemsShipped         | int(10)      | YES  |     | NULL                |                             |
| ShipServiceLevel             | varchar(100) | YES  |     | NULL                |                             |
| OrderStatus                  | varchar(50)  | YES  |     | NULL                |                             |
| SalesChannel                 | varchar(100) | YES  |     | NULL                |                             |
| ShippedByAmazonTFM           | varchar(10)  | YES  |     | NULL                |                             |
| IsBusinessOrder              | varchar(10)  | YES  |     | NULL                |                             |
| LatestDeliveryDate           | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| NumberOfItemsUnshipped       | int(10)      | YES  |     | NULL                |                             |
| PaymentMethodDetail          | varchar(50)  | YES  |     | NULL                |                             |
| BuyerName                    | varchar(100) | YES  |     | NULL                |                             |
| EarliestDeliveryDate         | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| CurrencyCode                 | varchar(10)  | YES  |     | NULL                |                             |
| Amount                       | float        | YES  |     | NULL                |                             |
| IsPremiumOrder               | varchar(10)  | YES  |     | NULL                |                             |
| EarliestShipDate             | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
| MarketplaceId                | varchar(50)  | YES  |     | NULL                |                             |
| FulfillmentChannel           | varchar(50)  | YES  |     | NULL                |                             |
| PurchaseOrderNumber          | varchar(50)  | YES  |     | NULL                |                             |
| PaymentMethod                | varchar(50)  | YES  |     | NULL                |                             |
| City                         | varchar(100) | YES  |     | NULL                |                             |
| AddressType                  | varchar(50)  | YES  |     | NULL                |                             |
| PostalCode                   | varchar(50)  | YES  |     | NULL                |                             |
| StateOrRegion                | varchar(100) | YES  |     | NULL                |                             |
| Phone                        | varchar(50)  | YES  |     | NULL                |                             |
| CountryCode                  | varchar(50)  | YES  |     | NULL                |                             |
| Name                         | varchar(100) | YES  |     | NULL                |                             |
| AddressLine1                 | varchar(500) | YES  |     | NULL                |                             |
| AddressLine2                 | varchar(500) | YES  |     | NULL                |                             |
| IsPrime                      | varchar(10)  | YES  |     | NULL                |                             |
| ShipmentServiceLevelCategory | varchar(50)  | YES  |     | NULL                |                             |
| SellerOrderId                | varchar(50)  | YES  |     | NULL                |                             |
| Seller                       | varchar(100) | YES  |     | NULL                |                             |
| RequestId_1                  | varchar(50)  | YES  |     | NULL                | ListOrders' RequestId       |
| RequestId_2                  | varchar(50)  | YES  |     | NULL                | ListOrderItems' RequestId   |
+------------------------------+--------------+------+-----+---------------------+-----------------------------+


