# -*- coding: utf-8 -*-
"""
Created at: 18-1-12 上午11:37

@Author: Qian
"""

from my_modules import mysqlconn


def create_orders_table():
    create_table_sql = """CREATE TABLE IF NOT EXISTS `amazon_orders` (
      `AmazonOrderId` varchar(50) NOT NULL,
      `LastUpdateDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `ASIN` varchar(50) NOT NULL,
      `SellerSKU` varchar(50) DEFAULT NULL,
      `PaidDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `LatestShipDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `OrderType` varchar(50) DEFAULT NULL,
      `PurchaseDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `BuyerEmail` varchar(100) DEFAULT NULL,
      `IsReplacementOrder` varchar(10) DEFAULT NULL,
      `NumberOfItemsShipped` int(10) DEFAULT NULL,
      `ShipServiceLevel` varchar(100) DEFAULT NULL,
      `OrderStatus` varchar(50) DEFAULT NULL,
      `SalesChannel` varchar(100) DEFAULT NULL,
      `ShippedByAmazonTFM` varchar(10) DEFAULT NULL,
      `IsBusinessOrder` varchar(10) DEFAULT NULL,
      `LatestDeliveryDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `NumberOfItemsUnshipped` int(10) DEFAULT NULL,
      `PaymentMethodDetail` varchar(50) DEFAULT NULL,
      `BuyerName` varchar(100) DEFAULT NULL,
      `EarliestDeliveryDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `CurrencyCode` varchar(10) DEFAULT NULL,
      `Amount` float DEFAULT NULL,
      `IsPremiumOrder` varchar(10) DEFAULT NULL,
      `EarliestShipDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `MarketplaceId` varchar(50) DEFAULT NULL,
      `FulfillmentChannel` varchar(50) DEFAULT NULL,
      `PurchaseOrderNumber` varchar(50) DEFAULT NULL,
      `PaymentMethod` varchar(50) DEFAULT NULL,
      `City` varchar(100) DEFAULT NULL,
      `AddressType` varchar(50) DEFAULT NULL,
      `PostalCode` varchar(50) DEFAULT NULL,
      `StateOrRegion` varchar(100) DEFAULT NULL,
      `Phone` varchar(50) DEFAULT NULL,
      `CountryCode` varchar(50) DEFAULT NULL,
      `Name` varchar(100) DEFAULT NULL,
      `AddressLine1` varchar(500) DEFAULT NULL,
      `AddressLine2` varchar(500) DEFAULT NULL,
      `IsPrime` varchar(10) DEFAULT NULL,
      `ShipmentServiceLevelCategory` varchar(50) DEFAULT NULL,
      `SellerOrderId` varchar(50) DEFAULT NULL,
      `Seller` varchar(100) DEFAULT NULL,
      `RequestId_1` varchar(50) DEFAULT NULL,
      `RequestId_2` varchar(50) DEFAULT NULL,
      PRIMARY KEY (`AmazonOrderId`,`LastUpdateDate`,`ASIN`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    conn = mysqlconn.mysqlconn()
    r = conn.cursor().execute(create_table_sql)
    conn.close()
    return r


if __name__ == "__main__":
    pass
