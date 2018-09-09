# -*- coding: utf-8 -*-
"""
Created at: 18-4-25 上午7:21

@Author: Qian
"""

'''
XML Parse Rules
'''

# Orders
LIST_ORDERS = {
    'Common_Info': ['RequestId', 'NextToken', ],
    'RequestId': './ResponseMetadata/RequestId',
    'NextToken': './ListOrdersResult/NextToken',
    'CreatedBefore': './ListOrdersResult/CreatedBefore',

    'results': './ListOrdersResult/Orders',
    'result_list': './Order',

    # the keys in `Not_In` list are not the primary info of Order
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'NextToken', 'CreatedBefore', 'results', 'result_list', ],
    'AmazonOrderId': './AmazonOrderId',
    'LastUpdateDate': './LastUpdateDate',
    'PurchaseDate': './PurchaseDate',
    'Amount': './OrderTotal/Amount',
    'CurrencyCode': './OrderTotal/CurrencyCode',
    'OrderType': './OrderType',
    'OrderStatus': './OrderStatus',
    'SalesChannel': './SalesChannel',
    'NumberOfItemsShipped': './NumberOfItemsShipped',
    'NumberOfItemsUnshipped': './NumberOfItemsUnshipped',
    'BuyerEmail': './BuyerEmail',
    'BuyerName': './BuyerName',
    'Name': './ShippingAddress/Name',
    'Phone': './ShippingAddress/Phone',
    'CountryCode': './ShippingAddress/CountryCode',
    'StateOrRegion': './ShippingAddress/StateOrRegion',
    'City': './ShippingAddress/City',
    'PostalCode': './ShippingAddress/PostalCode',
    'AddressLine1': './ShippingAddress/AddressLine1',
    'AddressLine2': './ShippingAddress/AddressLine2',
    'AddressType': './ShippingAddress/AddressType',
    'EarliestShipDate': './EarliestShipDate',
    'LatestShipDate': './LatestShipDate',
    'EarliestDeliveryDate': './EarliestDeliveryDate',
    'LatestDeliveryDate': './LatestDeliveryDate',
    'ShipServiceLevel': './ShipServiceLevel',
    'ShipmentServiceLevelCategory': './ShipmentServiceLevelCategory',
    'ShippedByAmazonTFM': './ShippedByAmazonTFM',
    'MarketplaceId': './MarketplaceId',
    'IsPrime': './IsPrime',
    'IsPremiumOrder': './IsPremiumOrder',
    'IsBusinessOrder': './IsBusinessOrder',
    'IsReplacementOrder': './IsReplacementOrder',
    'PaymentMethod': './PaymentMethod',
    'PaymentMethodDetail': './PaymentMethodDetails/PaymentMethodDetail',
    'FulfillmentChannel': './FulfillmentChannel',
    'SellerOrderId': './SellerOrderId',
}

LIST_ORDER_ITEMS = {
    'Common_Info': ['RequestId', 'AmazonOrderId', ],
    'RequestId': './ResponseMetadata/RequestId',
    'AmazonOrderId': './ListOrderItemsResult/AmazonOrderId',

    'results': './ListOrderItemsResult/OrderItems',
    'result_list': './OrderItem',

    # the keys in `Not_In` list are not the primary info of OrderItem
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'AmazonOrderId', 'results', 'result_list', ],
    'SellerSKU': './SellerSKU',
    'ASIN': './ASIN',
    'OrderItemId': './OrderItemId',
    'QuantityOrdered': './QuantityOrdered',
    'QuantityShipped': './QuantityShipped',
    'ConditionId': './ConditionId',
    'IsGift': './IsGift',
    'ItemPrice_Amount': './ItemPrice/Amount',
    'ItemPrice_CurrencyCode': './ItemPrice/CurrencyCode',
    'ItemTax_Amount': './ItemTax/Amount',
    'ItemTax_CurrencyCode': './ItemTax/CurrencyCode',
    'ShippingPrice_Amount': './ShippingPrice/Amount',
    'ShippingPrice_CurrencyCode': './ShippingPrice/CurrencyCode',
    'ShippingTax_Amount': './ShippingTax/Amount',
    'ShippingTax_CurrencyCode': './ShippingTax/CurrencyCode',
    'ShippingDiscount_Amount': './ShippingDiscount/Amount',
    'ShippingDiscount_CurrencyCode': './ShippingDiscount/CurrencyCode',
    'PromotionDiscount_Amount': './PromotionDiscount/Amount',
    'PromotionDiscount_CurrencyCode': './PromotionDiscount/CurrencyCode',
}

# Fulfillment
LIST_INVENTORY_SUPPLY = {
    'Common_Info': ['RequestId', 'MarketplaceId', ],
    'RequestId': './ResponseMetadata/RequestId',
    'MarketplaceId': './ListInventorySupplyResult/MarketplaceId',

    'results': './ListInventorySupplyResult/InventorySupplyList',
    'result_list': './member',

    # the keys in `Not_In` list are not the primary info of member
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'MarketplaceId', 'results', 'result_list', ],
    'SellerSKU': './SellerSKU',
    'ASIN': './ASIN',
    'FNSKU': './FNSKU',
    'InStockSupplyQuantity': './InStockSupplyQuantity',
    'Condition': './Condition',
}

# Reports
REQUEST_REPORT = {
    'Common_Info': ['RequestId', ],
    'RequestId': './ResponseMetadata/RequestId',

    'results': './RequestReportResult',
    'result_list': './ReportRequestInfo',

    # the keys in `Not_In` list are not the primary info of ReportRequestInfo
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'results', 'result_list', ],
    'ReportType': './ReportType',
    'ReportProcessingStatus': './ReportProcessingStatus',
    'ReportRequestId': './ReportRequestId',
}

GET_REPORT_REQUEST_LIST = {
    'Common_Info': ['RequestId', 'NextToken', ],
    'RequestId': './ResponseMetadata/RequestId',
    'HasNext': './GetReportRequestListResult/HasNext',
    'NextToken': './GetReportRequestListResult/NextToken',

    'results': './GetReportRequestListResult',
    'result_list': './ReportRequestInfo',

    # the keys in `Not_In` list are not the primary info of ReportRequestInfo
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'HasNext', 'NextToken', 'results', 'result_list', ],
    'ReportType': './ReportType',
    'ReportRequestId': './ReportRequestId',
    'ReportProcessingStatus': './ReportProcessingStatus',
    'GeneratedReportId': './GeneratedReportId',
}

GET_REPORT = {}

# Products
GET_MY_PRICE_FOR_SKU = {
    'Common_Info': ['RequestId', ],
    'RequestId': './ResponseMetadata/RequestId',

    'results': '.',
    'result_list': './GetMyPriceForSKUResult',

    # the keys in `Not_In` list are not the primary info of ReportRequestInfo
    'Not_In': ['Not_In', 'Common_Info', 'RequestId', 'results', 'result_list', ],
    'SellerSKU': './Product/Identifiers/SKUIdentifier/SellerSKU',
    'SellerId': './Product/Identifiers/SKUIdentifier/SellerId',
    'MarketplaceId': './Product/Identifiers/SKUIdentifier/MarketplaceId',
    'ASIN': './Product/Identifiers/MarketplaceASIN/ASIN',
    'LandedPrice_Amount': './Product/Offers/Offer/BuyingPrice/LandedPrice/Amount',
    'LandedPrice_CurrencyCode': './Product/Offers/Offer/BuyingPrice/LandedPrice/CurrencyCode',
    'ListingPrice_Amount': './Product/Offers/Offer/BuyingPrice/ListingPrice/Amount',
    'ListingPrice_CurrencyCode': './Product/Offers/Offer/BuyingPrice/ListingPrice/CurrencyCode',
    'Shipping_Amount': './Product/Offers/Offer/BuyingPrice/Shipping/Amount',
    'Shipping_CurrencyCode': './Product/Offers/Offer/BuyingPrice/Shipping/CurrencyCode',
    'RegularPrice_Amount': './Product/Offers/Offer/RegularPrice/Amount',
    'RegularPrice_CurrencyCode': './Product/Offers/Offer/RegularPrice/CurrencyCode',
    'FulfillmentChannel': './Product/Offers/Offer/FulfillmentChannel',
    'ItemCondition': './Product/Offers/Offer/ItemCondition',
    'ItemSubCondition': './Product/Offers/Offer/ItemSubCondition',
}
