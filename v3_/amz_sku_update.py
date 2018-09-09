# -*- coding: utf-8 -*-
"""
Created at: 18-4-26 上午10:02

@Author: Qian
"""

import os
from my_modules import mysqlconn

from handlers import update_mysku
from BasicConfig.mysql_info import db_config
from BasicConfig.account_info import ACCOUNT_INFO

import logging
from logging import config
dir_path = os.path.dirname(__file__)  # relative path, it wil get '' when run it in its dir
config.fileConfig(os.path.join(dir_path, 'BasicConfig/AmazonLogging.conf'))


# 将sku表中非FBA产品的库存同步到inventory表中
def sku_to_inventory(logger):
    sql = "select sku,Seller,MarketplaceId,quantity from sku where quantity is not NULL;"

    try:
        conn = mysqlconn.mysqlconn(**db_config)
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
    except:
        logger.exception("db Error")
    else:
        for i in data:
            _data = {'SellerSKU': i[0], 'Seller': i[1], 'MarketplaceId': i[2], 'InStockSupplyQuantity': i[3], }
            try:
                mysqlconn.db_update(conn, _data, ['SellerSKU', 'Seller', 'MarketplaceId'], 'inventory')
            except:
                logger.exception(_data)
    finally:
        conn.close()


def main(logger, Account, market_list=tuple(), ReportType=None):
    if not market_list:
        market_list = tuple([Account[key] for key in Account if key.startswith('MarketplaceId')])
    if not ReportType:
        ReportType = "_GET_FLAT_FILE_OPEN_LISTINGS_DATA_"

    conn = mysqlconn.mysqlconn(**db_config)

    result = []
    for MarketplaceId in market_list:
        try:
            logger.info(MarketplaceId + "\t" + ReportType + "\tStart")
            result.append(update_mysku(conn, Account, MarketplaceId, ReportType))
        except:
            logger.exception(MarketplaceId + "\t" + ReportType + "\tError")

    conn.close()
    return result


if __name__ == '__main__':
    logger = logging.getLogger('main')
    logger.info("Update SKU")

    result = []
    for Seller in ACCOUNT_INFO:
        Account = ACCOUNT_INFO[Seller]
        logger.info(Account['Seller'] + "\tStart")
        result.append({Account['Seller']: main(logger, Account)})
    logger.debug(result)

    logger.info("sku_to_inventory Start")
    sku_to_inventory(logger)

    logger.info("All End")
