DROP DATABASE IF EXISTS `ciwei_db`;
CREATE DATABASE `ciwei_db` DEFAULT CHARACTER SET = `utf8mb4` collate `utf8mb4_general_ci`;
USE `ciwei_db`;
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables member  --outfile "common/models/jmall/Member.py"  --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables report  --outfile "common/models/ciwei/Report.py" --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables order  --outfile "common/models/ciwei/Order.py" --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables qr_code  --outfile "common/models/ciwei/QrCode.py" --flask
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables goods  --outfile "common/models/ciwei/Goods.py" --flask
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

# CREATE TABLE `address`(
#     `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
#     `member_id`  int(11) unsigned NOT NULL COMMENT '会员id',
#     `openid` varchar(80) NOT NULL DEFAULT '' COMMENT '第三方id',
#     `city_name` varchar(10) NOT NULL DEFAULT '' COMMENT '城市',
#     `county_name` varchar(10) NOT NULL DEFAULT '' COMMENT '区',
#     `province_name` varchar(10) NOT NULL DEFAULT '' COMMENT '省',
#     `national_code` varchar(10) NOT NULL DEFAULT '' COMMENT '省号',
#     `postal_code` varchar(10) NOT NULL DEFAULT '' COMMENT '邮政编码',
#     `detail_info` varchar(10) NOT NULL DEFAULT '' COMMENT '城市',
#     `tel_number` varchar(15) NOT NULL DEFAULT '' COMMENT '手机',
#     `user_name` varchar(15) NOT NULL DEFAULT '' COMMENT '收货人'
# )ENGINE =InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '地址';
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

DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL  COMMENT '会员id',
  `openid` varchar(80) NOT NULL DEFAULT '' COMMENT '第三方id',
  `transaction_id` varchar(64) DEFAULT '' COMMENT '微信支付交易号',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '支付金额',
  `status` tinyint(1) NOT NULL DEFAULT '-1' COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp COMMENT '支付完成时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信支付的订单';

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