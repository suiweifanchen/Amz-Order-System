
数据库的结构：
[database]
amazon


[table]
1. orders
----- structure -----
+------------------------------+--------------+------+-----+---------------------+-------+
| Field                        | Type         | Null | Key | Default             | Extra |
+------------------------------+--------------+------+-----+---------------------+-------+
| AmazonOrderId                | varchar(50)  | NO   | PRI | NULL                |       |
| Seller                       | varchar(100) | YES  |     | NULL                |       |
| LastUpdateDate               | timestamp    | NO   | PRI | 0000-00-00 00:00:00 |       |
| PurchaseDate                 | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| PaidDate                     | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| Amount                       | float        | YES  |     | NULL                |       |
| CurrencyCode                 | varchar(10)  | YES  |     | NULL                |       |
| OrderType                    | varchar(50)  | YES  |     | NULL                |       |
| OrderStatus                  | varchar(50)  | YES  |     | NULL                |       |
| SalesChannel                 | varchar(100) | YES  |     | NULL                |       |
| NumberOfItemsShipped         | int(10)      | YES  |     | NULL                |       |
| NumberOfItemsUnshipped       | int(10)      | YES  |     | NULL                |       |
| BuyerEmail                   | varchar(100) | YES  |     | NULL                |       |
| BuyerName                    | varchar(100) | YES  |     | NULL                |       |
| Name                         | varchar(100) | YES  |     | NULL                |       |
| Phone                        | varchar(50)  | YES  |     | NULL                |       |
| CountryCode                  | varchar(50)  | YES  |     | NULL                |       |
| StateOrRegion                | varchar(100) | YES  |     | NULL                |       |
| City                         | varchar(100) | YES  |     | NULL                |       |
| PostalCode                   | varchar(50)  | YES  |     | NULL                |       |
| AddressLine1                 | varchar(500) | YES  |     | NULL                |       |
| AddressLine2                 | varchar(500) | YES  |     | NULL                |       |
| EarliestShipDate             | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| LatestShipDate               | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| LatestDeliveryDate           | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| EarliestDeliveryDate         | timestamp    | NO   |     | 0000-00-00 00:00:00 |       |
| ShipServiceLevel             | varchar(100) | YES  |     | NULL                |       |
| ShipmentServiceLevelCategory | varchar(50)  | YES  |     | NULL                |       |
| ShippedByAmazonTFM           | varchar(10)  | YES  |     | NULL                |       |
| MarketplaceId                | varchar(50)  | YES  |     | NULL                |       |
| IsPrime                      | varchar(10)  | YES  |     | NULL                |       |
| IsPremiumOrder               | varchar(10)  | YES  |     | NULL                |       |
| IsBusinessOrder              | varchar(10)  | YES  |     | NULL                |       |
| IsReplacementOrder           | varchar(10)  | YES  |     | NULL                |       |
| PaymentMethod                | varchar(50)  | YES  |     | NULL                |       |
| PaymentMethodDetail          | varchar(50)  | YES  |     | NULL                |       |
| FulfillmentChannel           | varchar(50)  | YES  |     | NULL                |       |
| SellerOrderId                | varchar(50)  | YES  |     | NULL                |       |
| RequestId                    | varchar(50)  | YES  |     | NULL                |       |
+------------------------------+--------------+------+-----+---------------------+-------+

2. orderitems
----- structure -----
+-----------------+-------------+------+-----+---------+-------+
| Field           | Type        | Null | Key | Default | Extra |
+-----------------+-------------+------+-----+---------+-------+
| AmazonOrderId   | varchar(50) | NO   | PRI | NULL    |       |
| SellerSKU       | varchar(50) | NO   | PRI | NULL    |       |
| ASIN            | varchar(50) | NO   |     | NULL    |       |
| QuantityOrdered | int(10)     | YES  |     | -1      |       |
| ConditionId     | varchar(10) | YES  |     | NULL    |       |
| IsGift          | varchar(10) | YES  |     | NULL    |       |
| ItemPrice       | float       | YES  |     | NULL    |       |
| CurrencyCode_IP | varchar(10) | YES  |     | NULL    |       |
| RequestId       | varchar(50) | YES  |     | NULL    |       |
+-----------------+-------------+------+-----+---------+-------+

3. inventory
----- structure -----
+-----------------+-------------+------+-----+---------+-------+
| Field           | Type        | Null | Key | Default | Extra |
+-----------------+-------------+------+-----+---------+-------+
| SellerSKU       | varchar(50) | NO   | PRI | NULL    |       |
| ASIN            | varchar(50) | YES  |     | NULL    |       |
| InStockQuantity | int(10)     | YES  |     | -1      |       |
| Condition       | varchar(50) | YES  |     | NULL    |       |
| MarketplaceId   | varchar(50) | YES  |     | NULL    |       |
| RequestId       | varchar(50) | YES  |     | NULL    |       |
+-----------------+-------------+------+-----+---------+-------+
