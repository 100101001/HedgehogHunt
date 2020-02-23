DROP DATABASE IF EXISTS `ciwei_db`;
CREATE DATABASE `ciwei_db` DEFAULT CHARACTER SET = `utf8mb4` collate `utf8mb4_general_ci`;
USE `ciwei_db`;
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables member  --outfile "common/models/jmall/Member.py"  --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables report  --outfile "common/models/ciwei/Report.py" --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables order  --outfile "common/models/ciwei/Order.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables qr_code  --outfile "common/models/ciwei/QrCode.py" --flask

# 新增匹配数字段
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables goods  --outfile "common/models/ciwei/Goods.py" --flask
# 购物页新增表
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables campus  --outfile "common/models/ciwei/mall/Campus.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables product  --outfile "common/models/ciwei/mall/Product.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables product_cat  --outfile "common/models/ciwei/mall/ProductCat.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables campus_product  --outfile "common/models/ciwei/mall/CampusProduct.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables product_comments  --outfile "common/models/ciwei/mall/ProductComments.py" --flask
# 购物车新增表
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables cart  --outfile "common/models/ciwei/mall/Cart.py" --flask
# 订单页新增表
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables order_product  --outfile "common/models/ciwei/mall/OrderProduct.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables address  --outfile "common/models/ciwei/mall/Address.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables order  --outfile "common/models/ciwei/mall/Order.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables product_stock_change_log  --outfile "common/models/ciwei/mall/ProductStockChangeLog.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables product_sale_change_log  --outfile "common/models/ciwei/mall/ProductSaleChangeLog.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables queue_list  --outfile "common/models/ciwei/mall/QueueList.py" --flask
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables order_callback_data  --outfile "common/models/ciwei/mall/OrderCallBackData.py" --flask
# 感谢酬金修改表名
# flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables thank_order  --outfile "common/models/ciwei/ThankOrder.py" --flask


DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `uid` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '管理员id',
  `member_id` int(11) unsigned NOT NULL  COMMENT '注册会员id',
  `level` int(11) unsigned NOT NULL  COMMENT '管理员等级',
  `name` varchar(100) NOT NULL DEFAULT '' COMMENT '用户名',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `email` varchar(100) NOT NULL DEFAULT '' COMMENT '邮箱地址',
  `sex` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1：男 2：女 0：没填写',
  `avatar` varchar(200) NOT NULL DEFAULT '' COMMENT '头像',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1：有效 0：无效',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';


DROP TABLE IF EXISTS `member`;
CREATE TABLE `member` (
  `id` int(11) unsigned NOT NULL  AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '拉黑会员的管理员id',
  `qr_code_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '小程序二维码id',
  `nickname` varchar(100) NOT NULL DEFAULT '' COMMENT '会员名',
  `salt` varchar(255) NOT NULL DEFAULT '' COMMENT '加密生成的字符串',
  `credits` int(11) NOT NULL DEFAULT '0' COMMENT '会员积分',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '注册会员的姓名，用于后期做匹配',
  `location` varchar(255) NOT NULL DEFAULT '' COMMENT '会员收货地址',
  `sex` tinyint(1) NOT NULL DEFAULT '0' COMMENT '性别 1：男 2：女',
  `avatar` varchar(200) NOT NULL DEFAULT '' COMMENT '会员头像',
  `qr_code` varchar(200) NOT NULL DEFAULT '' COMMENT '会员的小程序二维码',
  `openid` varchar(80) NOT NULL DEFAULT '' COMMENT '第三方id',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `mark_id` varchar(1000) NOT NULL DEFAULT '' COMMENT '用户认领的物品id,字符串',
  `gotback_id` varchar(2000) NOT NULL DEFAULT '' COMMENT '用户最终取回的物品id,字符串',
  `recommend_id` varchar(3000) NOT NULL DEFAULT '' COMMENT '系统推荐的物品id,字符串',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员表';

ALTER TABLE member AUTO_INCREMENT = 100000;

# CREATE TABLE `recommend`(
#     `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
#     `lost_goods_id` int(11) unsigned NOT NULL COMMENT '失物ID',
#     `found_goods_id` int(11) unsigned NOT NULL COMMENT '拾物ID',
#     `lost_openid` int(11) unsigned NOT NULL COMMENT '失物openID',
#     `found_openid` int(11) unsigned NOT NULL COMMENT '拾物openID',
#     `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '状态 1：已查看 0：未查看',
#     `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
#     `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
#     PRIMARY KEY (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='匹配推荐';

DROP TABLE IF EXISTS `address`;
CREATE TABLE `address` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL DEFAULT '0' COMMENT '会员id',
  `nickname` varchar(20) NOT NULL DEFAULT '' COMMENT '收货人姓名',
  `mobile` varchar(11) NOT NULL DEFAULT '' COMMENT '收货人手机号码',
  `province_id` int(11) NOT NULL DEFAULT '0' COMMENT '省id',
  `province_str` varchar(50) NOT NULL DEFAULT '' COMMENT '省名称',
  `city_id` int(11) NOT NULL DEFAULT '0' COMMENT '城市id',
  `city_str` varchar(50) NOT NULL DEFAULT '' COMMENT '市名称',
  `area_id` int(11) NOT NULL DEFAULT '0' COMMENT '区域id',
  `area_str` varchar(50) NOT NULL DEFAULT '' COMMENT '区域名称',
  `address` varchar(100) NOT NULL DEFAULT '' COMMENT '详细地址',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否有效 1：有效 0：无效',
  `is_default` TINYINT(1)  NOT NULL  DEFAULT '0'  COMMENT '默认地址',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_member_id_status` (`member_id`,`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员收货地址';

DROP TABLE IF EXISTS `qr_code`;
CREATE TABLE `qr_code` (
  `id` int(11) unsigned NOT NULL  AUTO_INCREMENT,
  `member_id` int(11) unsigned COMMENT '二维码注册会员id',
  `openid` varchar(80) NOT NULL DEFAULT '' COMMENT '第三方id',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '注册会员手机号码',
  `order_id` int(11) unsigned COMMENT '微信支付的订单id',
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '注册会员的姓名，用于后期做匹配',
  `location` varchar(255) NOT NULL DEFAULT '' COMMENT '注册会员收货地址',
  `qr_code` varchar(255) NOT NULL COMMENT '会员的小程序二维码图片',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二维码表';

DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '拉黑会员的管理员id',
  `member_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '发布消息的会员id',
  `openid` varchar(80) NOT NULL DEFAULT '' COMMENT '第三方id',
  `qr_code_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '扫描上传信息的二维码id',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `owner_id` varchar(20) NOT NULL DEFAULT '' COMMENT '最终取回物品的会员id,还是换成字符串吧',
  `name` varchar(80) NOT NULL DEFAULT '' COMMENT '商品名称',
  `owner_name` varchar(100) NOT NULL DEFAULT '' COMMENT '物主姓名',
  `location` varchar(100) NOT NULL DEFAULT '' COMMENT '物品放置地址',
  `target_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '悬赏金额',
  `main_image` varchar(100) NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) NOT NULL DEFAULT '' COMMENT '组图',
  `summary` varchar(1000) NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) UNSIGNED NOT NULL DEFAULT '7' COMMENT '1:待, 2:预, 3:已, 5:管理员删, 7:发布者创建中, 8:发布者被管理员拉黑',
  `recommended_times` int(11) NOT NULL DEFAULT '0' COMMENT '总匹配过失/拾物次数',
  `report_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '被举报后的状态，用于存储举报的状态值',
  `business_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：失物招领 0：寻物启事',
  `view_count` int(11) NOT NULL DEFAULT '0' COMMENT '总浏览次数',
  `tap_count` int(11) NOT NULL DEFAULT '0' COMMENT '查看地址次数',
  `mark_id` varchar(400) NOT NULL DEFAULT '' COMMENT '点击获取或者提交的用户id,列表',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品表';


DROP TABLE IF EXISTS `advs`;
CREATE TABLE `advs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '通过审核的管理员id',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '发布的物品的id',
  `member_id` int(11) unsigned NOT NULL  COMMENT '发布消息的会员id',
  `order_id` int(11) unsigned NOT NULL  COMMENT '微信支付的订单id',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已付款 0：未付款或者已过期',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `end_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '置顶的消失时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='顶部导航栏的广告表，按天收费，先提交并付费，管理员审核通过后发布，否则返还钱';


DROP TABLE IF EXISTS `report`;
CREATE TABLE `report` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '拉黑会员的管理员id',
  `member_id` int(11) unsigned NOT NULL  COMMENT '发布消息的会员id',
  `report_member_id` int(11) unsigned NOT NULL  COMMENT '举报消息的会员id',
  `record_id` int(11) NOT NULL COMMENT '信息id，有可能是物品信息违规，也可能是用户的答谢违规',
  `summary` varchar(200) NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
  `record_type` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：物品信息违规 0：答谢信息违规',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='举报消息表';

DROP TABLE IF EXISTS `thanks`;
CREATE TABLE `thanks` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '拉黑会员的管理员id',
  `member_id` int(11) unsigned NOT NULL  COMMENT '发布感谢的会员id',
  `order_id` int(11) unsigned NOT NULL  COMMENT '微信支付的订单id',
  `target_member_id` int(11) unsigned NOT NULL  COMMENT '接受消息的会员id',
  `goods_id` int(11) NOT NULL COMMENT '物品id',
  `summary` varchar(200) NOT NULL DEFAULT '' COMMENT '描述',
  `goods_name` varchar(30) NOT NULL DEFAULT '' COMMENT '物品名称',
  `business_desc` varchar(10) NOT NULL DEFAULT '' COMMENT '拾到或者丢失',
  `owner_name` varchar(80) NOT NULL DEFAULT '' COMMENT '用户的名称，可能只是微信昵称',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
  `report_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '被举报后的状态，用于存储举报的状态值',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答谢表';

DROP TABLE IF EXISTS `thank_order`;
CREATE TABLE `thank_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL COMMENT '会员id',
  `openid` varchar(32) NOT NULL COMMENT '下单微信用户',
  `transaction_id` varchar(64) DEFAULT '' COMMENT '微信支付交易号',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '支付金额',
  `status` tinyint(1) NOT NULL DEFAULT '-1' COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付完成时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答谢支付的订单';

DROP TABLE IF EXISTS `campus`;
CREATE TABLE `campus`(
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(80) NOT NULL DEFAULT '' COMMENT '大学名',
    `code` varchar(80) NOT NULL DEFAULT '' COMMENT '代号',
    `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大学表';

DROP TABLE IF EXISTS `campus_product`;
CREATE TABLE `campus_product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `campus_id` int(11) unsigned NOT NULL COMMENT '大学',
  `product_id` int(11) unsigned NOT NULL COMMENT '产品',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大学周边表';

DROP TABLE IF EXISTS `product`;
CREATE TABLE `product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `cat_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '周边类别',
  `name` varchar(80) NOT NULL DEFAULT '' COMMENT '周边名',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '单价',
  `main_image` varchar(100) NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) NOT NULL DEFAULT '' COMMENT '组图',
  `tags` varchar(200) NOT NULL DEFAULT '' COMMENT 'tag关键字，以'',''相连',
  `description` varchar(2000) NOT NULL DEFAULT '' COMMENT '详情描述',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `view_cnt` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '浏览量',
  `stock_cnt` int(11) unsigned NOT NULL DEFAULT '99999' COMMENT '库存量',
  `sale_cnt` int(11) NOT NULL DEFAULT '0' COMMENT '销售量',
  `comment_cnt` int(11) NOT NULL DEFAULT '0' COMMENT '评论量',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='周边表';


DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(40) NOT NULL DEFAULT '' COMMENT '随机订单号',
  `member_id` bigint(11) NOT NULL DEFAULT '0' COMMENT '会员id',
  `total_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '订单应付金额',
  `yun_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '运费金额',
  `pay_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '订单实付金额',
  `pay_sn` varchar(128) NOT NULL DEFAULT '' COMMENT '第三方流水号',
  `prepay_id` varchar(128) NOT NULL DEFAULT '' COMMENT '第三方预付id',
  `note` text NOT NULL COMMENT '备注信息',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '1：支付完成 0 无效 -1 申请退款 -2 退款中 -9 退款成功  -8 待支付  -7 完成支付待确认',
  `express_status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '快递状态，-8 待支付 -7 已付款待发货 1：确认收货 0：失败',
  `express_address_id` int(11) NOT NULL DEFAULT '0' COMMENT '快递地址id',
  `express_info` varchar(1000) NOT NULL DEFAULT '' COMMENT '快递信息',
  `comment_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '评论状态',
  `pay_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '付款到账时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最近一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_order_sn` (`order_sn`),
  KEY `idx_member_id_status` (`member_id`,`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='周边购买订单表';


DROP TABLE IF EXISTS `order_product`;
CREATE TABLE `order_product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `order_id` int(11) unsigned NOT NULL COMMENT '订单',
  `member_id` bigint(11) NOT NULL DEFAULT '0' COMMENT '会员id',
  `product_id` int(11) unsigned NOT NULL COMMENT '产品',
  `product_num` int(11) unsigned NOT NULL DEFAULT 1 COMMENT '购买数, 默认1份',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '商品总价格，售价 * 数量',
  `note` text NOT NULL COMMENT '备注信息',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态：1：成功 0 失败',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单包含的周边表';


DROP TABLE IF EXISTS `product_cat`;
CREATE TABLE `product_cat` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL DEFAULT '' COMMENT '类别名称',
  `weight` tinyint(4) NOT NULL DEFAULT '1' COMMENT '权重',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='周边分类';

DROP TABLE IF EXISTS `cart`;
CREATE TABLE `cart` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL COMMENT '会员的ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '产品',
  `product_num` int(11) unsigned NOT NULL COMMENT '产品数',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';

DROP TABLE IF EXISTS `product_comments`;
CREATE TABLE `product_comments` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL DEFAULT '0' COMMENT '会员id',
  `product_ids` varchar(200) NOT NULL DEFAULT '' COMMENT '商品ids',
  `order_id` int(11) NOT NULL DEFAULT '0' COMMENT '订单id',
  `score` tinyint(4) NOT NULL DEFAULT '0' COMMENT '评分',
  `content` varchar(200) NOT NULL DEFAULT '' COMMENT '评论内容',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员评论表';

DROP TABLE IF EXISTS `product_stock_change_log`;
CREATE TABLE `product_stock_change_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL COMMENT '商品id',
  `unit` int(11) NOT NULL DEFAULT '0' COMMENT '变更多少',
  `total_stock` int(11) NOT NULL DEFAULT '0' COMMENT '变更之后总量',
  `note` varchar(100) NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库存变更表';

DROP TABLE IF EXISTS `product_sale_change_log`;
CREATE TABLE `product_sale_change_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL DEFAULT '0' COMMENT '商品id',
  `quantity` int(11) NOT NULL DEFAULT '0' COMMENT '售卖数量',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '售卖金额',
  `member_id` int(11) NOT NULL DEFAULT '0' COMMENT '会员id',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '售卖时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品销售情况';


DROP TABLE IF EXISTS `queue_list`;
CREATE TABLE `queue_list` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `queue_name` varchar(30) NOT NULL DEFAULT '' COMMENT '队列名字',
  `data` varchar(500) NOT NULL DEFAULT '' COMMENT '队列数据',
  `status` tinyint(1) NOT NULL DEFAULT '-1' COMMENT '状态 -1 待处理 1 已处理',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件队列表';


DROP TABLE IF EXISTS `order_callback_data`;
CREATE TABLE `order_callback_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL DEFAULT '0' COMMENT '支付订单id',
  `pay_data` text NOT NULL COMMENT '支付回调信息',
  `refund_data` text NOT NULL COMMENT '退款回调信息',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信支付回调数据表';

DROP TABLE IF EXISTS `feedback`;
CREATE TABLE `feedback` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '处理反馈消息的管理员id',
  `member_id` int(11) unsigned NOT NULL  COMMENT '反馈消息的会员id',
  `summary` varchar(10000) NOT NULL DEFAULT '' COMMENT '描述',
  `main_image` varchar(100) NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) NOT NULL DEFAULT '' COMMENT '组图',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='反馈表';


DROP TABLE IF EXISTS `images`;
CREATE TABLE `images` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `file_key` varchar(60) NOT NULL DEFAULT '' COMMENT '文件名',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;