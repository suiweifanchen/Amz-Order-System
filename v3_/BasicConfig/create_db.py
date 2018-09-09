# -*- coding: utf-8 -*-
"""
Created at: 18-4-23 上午10:05

@Author: Qian
"""

import re
from my_modules import mysqlconn

from .mysql_info import db_config

__all__ = [
    'amazon_db_sql',
    'tables',
    'orders_table_sql', 'orders_fields',
    'orderitems_table_sql', 'orderitems_fields',
    'inventory_table_sql', 'inventory_fields',
    'sku_table_sql', 'sku_fields',
    'price_table_sql', 'price_fields',
]

tables = ['amazon', 'orders', 'orderitems', 'inventory', 'sku', 'price', ]

amazon_db_sql = "CREATE DATABASE IF NOT EXISTS `amazon_backup`;"

orders_table_sql = "CREATE TABLE IF NOT EXISTS `orders` (" \
                   "`AmazonOrderId` varchar(50) NOT NULL," \
                   "`LastUpdateDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`PurchaseDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`PaidDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`Seller` varchar(100) DEFAULT NULL," \
                   "`Amount` float DEFAULT NULL," \
                   "`CurrencyCode` varchar(10) DEFAULT NULL," \
                   "`OrderType` varchar(50) DEFAULT NULL," \
                   "`OrderStatus` varchar(50) DEFAULT NULL," \
                   "`SalesChannel` varchar(100) DEFAULT NULL," \
                   "`NumberOfItemsShipped` int(10) DEFAULT NULL," \
                   "`NumberOfItemsUnshipped` int(10) DEFAULT NULL," \
                   "`BuyerEmail` varchar(100) DEFAULT NULL," \
                   "`BuyerName` varchar(100) DEFAULT NULL," \
                   "`Name` varchar(100) DEFAULT NULL," \
                   "`Phone` varchar(50) DEFAULT NULL," \
                   "`CountryCode` varchar(50) DEFAULT NULL," \
                   "`StateOrRegion` varchar(100) DEFAULT NULL," \
                   "`City` varchar(100) DEFAULT NULL," \
                   "`PostalCode` varchar(50) DEFAULT NULL," \
                   "`AddressLine1` varchar(500) DEFAULT NULL," \
                   "`AddressLine2` varchar(500) DEFAULT NULL," \
                   "`AddressType` varchar(50) DEFAULT NULL," \
                   "`EarliestShipDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`LatestShipDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`EarliestDeliveryDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`LatestDeliveryDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'," \
                   "`ShipServiceLevel` varchar(100) DEFAULT NULL," \
                   "`ShipmentServiceLevelCategory` varchar(50) DEFAULT NULL," \
                   "`ShippedByAmazonTFM` varchar(10) DEFAULT NULL," \
                   "`MarketplaceId` varchar(50) DEFAULT NULL," \
                   "`IsPrime` varchar(10) DEFAULT NULL," \
                   "`IsPremiumOrder` varchar(10) DEFAULT NULL," \
                   "`IsBusinessOrder` varchar(10) DEFAULT NULL," \
                   "`IsReplacementOrder` varchar(10) DEFAULT NULL," \
                   "`PaymentMethod` varchar(50) DEFAULT NULL," \
                   "`PaymentMethodDetail` varchar(50) DEFAULT NULL," \
                   "`FulfillmentChannel` varchar(50) DEFAULT NULL," \
                   "`SellerOrderId` varchar(50) DEFAULT NULL," \
                   "`RequestId` varchar(50) DEFAULT NULL," \
                   "PRIMARY KEY (`AmazonOrderId`,`LastUpdateDate`)" \
                   ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

orderitems_table_sql = "CREATE TABLE IF NOT EXISTS `orderitems` (" \
                       "`AmazonOrderId` varchar(50) NOT NULL," \
                       "`SellerSKU` varchar(50) NOT NULL," \
                       "`ASIN` varchar(50) DEFAULT NULL," \
                       "`OrderItemId` varchar(50) DEFAULT NULL," \
                       "`QuantityOrdered` int(10) DEFAULT NULL," \
                       "`QuantityShipped` int(10) DEFAULT NULL," \
                       "`ConditionId` varchar(10) DEFAULT NULL," \
                       "`IsGift` varchar(10) DEFAULT NULL," \
                       "`ItemPrice_Amount` float DEFAULT NULL," \
                       "`ItemPrice_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`ItemTax_Amount` float DEFAULT NULL," \
                       "`ItemTax_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`ShippingPrice_Amount` float DEFAULT NULL," \
                       "`ShippingPrice_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`ShippingTax_Amount` float DEFAULT NULL," \
                       "`ShippingTax_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`ShippingDiscount_Amount` float DEFAULT NULL," \
                       "`ShippingDiscount_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`PromotionDiscount_Amount` float DEFAULT NULL," \
                       "`PromotionDiscount_CurrencyCode` varchar(10) DEFAULT NULL," \
                       "`RequestId` varchar(50) DEFAULT NULL," \
                       "PRIMARY KEY (`AmazonOrderId`, `SellerSKU`)" \
                       ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

inventory_table_sql = "CREATE TABLE IF NOT EXISTS `inventory` (" \
                      "`SellerSKU` varchar(50) NOT NULL," \
                      "`Seller` varchar(50) NOT NULL," \
                      "`MarketplaceId` varchar(50) NOT NULL," \
                      "`ASIN` varchar(50) DEFAULT NULL," \
                      "`FNSKU` varchar(50) DEFAULT NULL," \
                      "`InStockSupplyQuantity` int(10) DEFAULT NULL," \
                      "`Condition` varchar(50) DEFAULT NULL," \
                      "`RequestId` varchar(50) DEFAULT NULL," \
                      "PRIMARY KEY (`SellerSKU`, `Seller`, `MarketplaceId`)" \
                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

sku_table_sql = "CREATE TABLE IF NOT EXISTS `sku` (" \
                "`sku` varchar(50) NOT NULL," \
                "`Seller` varchar(50) NOT NULL," \
                "`MarketplaceId` varchar(50) NOT NULL," \
                "`asin` varchar(50) DEFAULT NULL," \
                "`price` float DEFAULT NULL," \
                "`BusinessPrice` float DEFAULT NULL," \
                "`quantity` int(10) DEFAULT NULL," \
                "`ReportId` varchar(50) DEFAULT NULL," \
                "PRIMARY KEY (`sku`, `Seller`, `MarketplaceId`)" \
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

price_table_sql = "CREATE TABLE IF NOT EXISTS `price` (" \
                  "`SellerSKU` varchar(50) NOT NULL," \
                  "`SellerId` varchar(50) NOT NULL," \
                  "`MarketplaceId` varchar(50) NOT NULL," \
                  "`Seller` varchar(50) DEFAULT NULL," \
                  "`ASIN` varchar(50) DEFAULT NULL," \
                  "`LandedPrice_Amount` float DEFAULT NULL," \
                  "`LandedPrice_CurrencyCode` varchar(10) DEFAULT NULL," \
                  "`ListingPrice_Amount` float DEFAULT NULL," \
                  "`ListingPrice_CurrencyCode` varchar(10) DEFAULT NULL," \
                  "`Shipping_Amount` float DEFAULT NULL," \
                  "`Shipping_CurrencyCode` varchar(10) DEFAULT NULL," \
                  "`RegularPrice_Amount` float DEFAULT NULL," \
                  "`RegularPrice_CurrencyCode` varchar(10) DEFAULT NULL," \
                  "`FulfillmentChannel` varchar(50) DEFAULT NULL," \
                  "`ItemCondition` varchar(10) DEFAULT NULL," \
                  "`ItemSubCondition` varchar(10) DEFAULT NULL," \
                  "`RequestId` varchar(50) DEFAULT NULL," \
                  "PRIMARY KEY (`SellerSKU`, `SellerId`, `MarketplaceId`)" \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"


def extract_kw(s):
    string = "\((.*)\)"
    pattern = re.compile(string)
    s = re.findall(pattern, s)[0]
    string = "`(.*?)` .+?,"
    pattern = re.compile(string)
    r = re.findall(pattern, s)
    return tuple(r)


orders_fields = extract_kw(orders_table_sql)
orderitems_fields = extract_kw(orderitems_table_sql)
inventory_fields = extract_kw(inventory_table_sql)
sku_fields = extract_kw(sku_table_sql)
price_fields = extract_kw(price_table_sql)


if __name__ == '__main__':
    pass
