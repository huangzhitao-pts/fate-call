# -*- coding: utf-8 -*-
import os


class DeployMentConfig(object):
    # mysql
    MYSQL_IP = os.getenv("MYSQL_IP", "192.168.89.155")
    MYSQL_PORT = os.getenv("MYSQL_PORT", 3370)
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "111")

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = \
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_IP}:{MYSQL_PORT}/federated_learning?charset=utf8"
    # SQLALCHEMY_POOL_SIZE = 20
    # SQLALCHEMY_POOL_RECYCLE = 1800
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "cc2913d6b5a123611d4e40b68f074ae5"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_BASE_DIR = os.path.join(BASE_DIR, "file_dir")

    LOCAL_ADDR_PORT = os.getenv("LOCAL_ADDR_PORT", "127.0.0.1:80")

    CPUT = 2  # 计算CPU利用率的时间间隔
    NETT = 2  # 计算网卡流量的时间间隔


config = {
    "deployment": DeployMentConfig
}
