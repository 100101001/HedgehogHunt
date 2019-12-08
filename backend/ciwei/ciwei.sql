DROP DATABASE IF EXISTS `ciwei_db`;
CREATE DATABASE `ciwei_db` DEFAULT CHARACTER SET = `utf8mb4`;
USE `ciwei_db`;
#flask-sqlacodegen "mysql://root:wcx9517530@127.0.0.1/ciwei_db" --tables member  --outfile "common/models/jmall/Member.py"  --flask
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
  `recommend_id` varchar(3000) NOT NULL DEFAULT '' COMMENT '系统推荐的物品id,字符串',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员表';

ALTER TABLE member AUTO_INCREMENT = 100000;


CREATE TABLE `qr_code` (
  `id` int(11) unsigned NOT NULL  AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL  COMMENT '二维码注册会员id',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '注册会员手机号码',
  `order_id` int(11) unsigned NOT NULL  COMMENT '微信支付的订单id',
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '注册会员的姓名，用于后期做匹配',
  `location` varchar(255) NOT NULL DEFAULT '' COMMENT '注册会员收货地址',
  `qr_code` blob NOT NULL COMMENT '会员的小程序二维码图片',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员表';

DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '拉黑会员的管理员id',
  `member_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '发布消息的会员id',
  `owner_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '最终取回物品的会员id',
  `qr_code_id` int(11) unsigned NOT NULL DEFAULT '0'  COMMENT '扫描上传信息的二维码id',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `name` varchar(80) NOT NULL DEFAULT '' COMMENT '商品名称',
  `owner_name` varchar(100) NOT NULL DEFAULT '' COMMENT '物主姓名',
  `location` varchar(100) NOT NULL DEFAULT '' COMMENT '物品放置地址',
  `target_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '悬赏金额',
  `main_image` varchar(100) NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) NOT NULL DEFAULT '' COMMENT '组图',
  `summary` varchar(1000) NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
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
  `goods_id` int(11) NOT NULL COMMENT '物品id',
  `summary` varchar(200) NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
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
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答谢表';

DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL  COMMENT '支付订单会员id',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '支付金额',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：已读 0：未读',
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