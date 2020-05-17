/*
 Navicat Premium Data Transfer

 Source Server         : opencs
 Source Server Type    : MySQL
 Source Server Version : 50727
 Source Host           : 47.102.201.193:3306
 Source Schema         : ciwei_db_test

 Target Server Type    : MySQL
 Target Server Version : 50727
 File Encoding         : 65001

 Date: 19/04/2020 19:55:30
*/
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for acs_sms_send_log
-- ----------------------------
DROP TABLE IF EXISTS `acs_sms_send_log`;
CREATE TABLE `acs_sms_send_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `biz_uuid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '本地业务ID',
  `trig_member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '触发发送短信的会员id',
  `trig_openid` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '触发发送短信的会员的第三方id',
  `rcv_member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '收短信的会员id',
  `rcv_openid` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '收短信的会员的第三方id',
  `phone_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '手机号',
  `sign_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '阿里云签名名称',
  `template_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '阿里云模板id',
  `params` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模板消息参数',
  `acs_resp_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用数据',
  `acs_product_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '阿里云产品名',
  `acs_request_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用请求ID',
  `acs_biz_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用业务ID',
  `acs_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用结果代码',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_acs_sms_send_log_uuid`(`biz_uuid`) USING BTREE,
  INDEX `ix_acs_sms_send_log_tmp_id`(`template_id`) USING BTREE COMMENT '模板ID，区分是否是验证码短信',
  INDEX `ix_acs_sms_send_log_phone_number`(`phone_number`) USING BTREE COMMENT '手机号',
  INDEX `ix_acs_sms_send_log_rcv_member_id`(`rcv_member_id`) USING BTREE,
  INDEX `ix_acs_sms_send_log_rcv_openid`(`rcv_openid`) USING BTREE COMMENT '收短信的会员第三方id'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '阿里云服务短信发送调用日志' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for address
-- ----------------------------
DROP TABLE IF EXISTS `address`;
CREATE TABLE `address`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL DEFAULT 0 COMMENT '会员id',
  `nickname` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '收货人姓名',
  `mobile` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '收货人手机号码',
  `province_id` int(11) NOT NULL DEFAULT 0 COMMENT '省id',
  `province_str` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '省名称',
  `city_id` int(11) NOT NULL DEFAULT 0 COMMENT '城市id',
  `city_str` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '市名称',
  `area_id` int(11) NOT NULL DEFAULT 0 COMMENT '区域id',
  `area_str` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '区域名称',
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '详细地址',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否有效 1：有效 0：无效',
  `is_default` tinyint(1) NOT NULL DEFAULT 0 COMMENT '默认地址',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_member_id_status`(`member_id`, `status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员收货地址' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for advs
-- ----------------------------
DROP TABLE IF EXISTS `advs`;
CREATE TABLE `advs`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `qr_code` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `stock` int(11) NOT NULL,
  `summary` varchar(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tap_count` int(11) NOT NULL,
  `target_price` decimal(10, 2) NOT NULL,
  `uu_id` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `view_count` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '顶部导航栏的广告表，按天收费，先提交并付费，管理员审核通过后发布，否则返还钱' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('4ace4fb400ea');

-- ----------------------------
-- Table structure for appeal
-- ----------------------------
DROP TABLE IF EXISTS `appeal`;
CREATE TABLE `appeal`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '申诉的物品id',
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '用户id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 0:待处理 1:已处理完毕',
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '系统指派处理的管理员id',
  `result` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '处理结果备注',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `deleted_by` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '删除申诉的管理员id',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_appeal_member_id`(`member_id`) USING BTREE,
  INDEX `ix_appeal_goods_id`(`goods_id`) USING BTREE,
  INDEX `ix_appeal_status`(`status`) USING BTREE,
  INDEX `ix_appeal_deleted_by`(`deleted_by`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '申诉表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for balance_order
-- ----------------------------
DROP TABLE IF EXISTS `balance_order`;
CREATE TABLE `balance_order`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '随机订单号',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '第三方id',
  `transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '微信支付交易号',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '支付金额',
  `status` tinyint(1) NOT NULL DEFAULT -1 COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付完成时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_balance_order_sn`(`order_sn`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '余额充值的订单' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for balance_order_callback_data
-- ----------------------------
DROP TABLE IF EXISTS `balance_order_callback_data`;
CREATE TABLE `balance_order_callback_data`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `balance_order_id` int(11) NOT NULL DEFAULT 0 COMMENT '支付订单id',
  `pay_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '支付回调信息',
  `refund_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '退款回调信息',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_obalance_order_callback_data_order_id`(`balance_order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '余额充值微信支付回调数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for campus
-- ----------------------------
DROP TABLE IF EXISTS `campus`;
CREATE TABLE `campus`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '大学名',
  `code` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '代号',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '大学表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of campus
-- ----------------------------
INSERT INTO `campus` VALUES (1, '同济大学', 'TJ', 'TJU.jpeg', '2020-02-20 12:20:29', '2020-02-20 12:20:29');

-- ----------------------------
-- Table structure for campus_product
-- ----------------------------
DROP TABLE IF EXISTS `campus_product`;
CREATE TABLE `campus_product`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `campus_id` int(11) UNSIGNED NOT NULL COMMENT '大学',
  `product_id` int(11) UNSIGNED NOT NULL COMMENT '产品',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_campus_product_campus_id`(`campus_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '大学周边表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of campus_product
-- ----------------------------
INSERT INTO `campus_product` VALUES (1, 1, 1, '2020-02-20 12:22:41', '2020-02-20 12:22:41');
INSERT INTO `campus_product` VALUES (2, 1, 2, '2020-02-20 12:22:55', '2020-02-20 12:22:55');
INSERT INTO `campus_product` VALUES (3, 1, 3, '2020-02-20 12:22:59', '2020-02-20 12:22:59');
INSERT INTO `campus_product` VALUES (4, 1, 4, '2020-03-02 20:05:53', '2020-03-02 20:05:53');
INSERT INTO `campus_product` VALUES (5, 1, 5, '2020-03-02 20:05:57', '2020-03-02 20:05:57');
INSERT INTO `campus_product` VALUES (6, 1, 6, '2020-03-02 20:25:50', '2020-03-02 20:25:50');
INSERT INTO `campus_product` VALUES (7, 1, 7, '2020-03-02 20:25:50', '2020-03-02 20:25:50');

-- ----------------------------
-- Table structure for cart
-- ----------------------------
DROP TABLE IF EXISTS `cart`;
CREATE TABLE `cart`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员的ID',
  `product_id` int(11) UNSIGNED NOT NULL COMMENT '产品',
  `product_num` int(11) UNSIGNED NOT NULL COMMENT '产品数',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_cart_member_id`(`member_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '购物车表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for feedback
-- ----------------------------
DROP TABLE IF EXISTS `feedback`;
CREATE TABLE `feedback`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '处理反馈消息的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '反馈消息的会员id',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '反馈消息的会员名',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '反馈消息的会员头像',
  `summary` varchar(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '组图',
  `views` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '阅读管理员id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_feedback_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '反馈表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for goods
-- ----------------------------
DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拉黑会员的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '发布消息的会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '发布消息的会员名',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '发布消息的会员头像',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `owner_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '最终取回物品的会员id',
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '商品名称',
  `owner_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物主姓名',
  `os_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物品发现和丢失地址',
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物品放置地址',
  `author_mobile` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '发布者实际的手机号',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '组图',
  `summary` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `business_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：失物招领 0：寻物启事',
  `qr_code_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '扫码归还的码主的openid',
  `return_goods_id` int(11) UNSIGNED NULL DEFAULT 0 COMMENT '归还的寻物启示ID',
  `return_goods_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '归还的寻物启示OPENID',
  `status` tinyint(1) NOT NULL DEFAULT 7 COMMENT '1:待, 2:预, 3:已, 5:管理员删, 7:发布者创建中, 8:发布者被管理员拉黑',
  `view_count` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '总浏览次数',
  `top_expire_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '置顶过期时间',
  `recommended_times` int(11) NOT NULL DEFAULT 1 COMMENT '总匹配过失/拾物次数',
  `report_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '被举报后的状态，用于存储举报的状态值',
  `confirm_time` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '线上确认时间',
  `finish_time` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '线下取回时间',
  `thank_time` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '答谢时间',
  `appeal_time` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申诉时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_goods_member_id`(`member_id`) USING BTREE,
  INDEX `ix_goods_status`(`status`) USING BTREE,
  INDEX `ix_goods_top_expire_time`(`top_expire_time`) USING BTREE,
  INDEX `ix_goods_view_count`(`view_count`) USING BTREE,
  INDEX `ix_goods_owner_id`(`owner_id`) USING BTREE,
  INDEX `ix_goods_qr_code_openid`(`qr_code_openid`) USING BTREE,
  INDEX `ix_goods_return_goods_openid`(`return_goods_openid`) USING BTREE,
  INDEX `ix_goods_business_type`(`business_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for goods_top_order
-- ----------------------------
DROP TABLE IF EXISTS `goods_top_order`;
CREATE TABLE `goods_top_order`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '随机订单号',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '第三方id',
  `transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '微信支付交易号',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '支付金额',
  `balance_discount` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '余额垫付金额',
  `status` tinyint(1) NOT NULL DEFAULT -1 COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付完成时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_goods_top_order_sn`(`order_sn`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品置顶支付的订单' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for goods_top_order_callback_data
-- ----------------------------
DROP TABLE IF EXISTS `goods_top_order_callback_data`;
CREATE TABLE `goods_top_order_callback_data`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `top_order_id` int(11) NOT NULL DEFAULT 0 COMMENT '支付订单id',
  `pay_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '支付回调信息',
  `refund_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '退款回调信息',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_order_callback_data_order_id`(`top_order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品置顶微信支付回调数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for images
-- ----------------------------
DROP TABLE IF EXISTS `images`;
CREATE TABLE `images`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `file_key` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '文件名',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '图片表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for mark
-- ----------------------------
DROP TABLE IF EXISTS `mark`;
CREATE TABLE `mark`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `business_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：失物招领 0：寻物启事',
  `goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '认领的物品id',
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '用户id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 0:未取 1:已取',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_mark_member_id`(`member_id`) USING BTREE,
  INDEX `ix_mark_goods_id`(`goods_id`) USING BTREE,
  INDEX `ix_mark_status`(`status`) USING BTREE,
  INDEX `ix_mark_business_type`(`business_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '认领表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member
-- ----------------------------
DROP TABLE IF EXISTS `member`;
CREATE TABLE `member`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拉黑会员的管理员id',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员名',
  `salt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '加密生成的字符串',
  `balance` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '用户账户余额',
  `credits` int(11) NOT NULL DEFAULT 0 COMMENT '会员积分',
  `mobile` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '注册会员的姓名，用于后期做匹配',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员收货地址',
  `sex` tinyint(1) NOT NULL DEFAULT 0 COMMENT '性别 1：男 2：女',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员头像',
  `qr_code` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员的小程序二维码',
  `left_notify_times` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '剩余通知次数',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：有效 0：无效',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_member_openid`(`openid`) USING BTREE,
  INDEX `ix_member_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100008 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100001, 0, '管理员', '', 4.73, 300, 'bPk3u33u+sqUiuxJ/+ubfQ==', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-04-19 00:10:04', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100002, 0, 'L  yx', '', 14.48, 520, 'FEuNz7OnlvGGiV3s9PN14A==', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-19 00:32:32', '2020-03-17 20:09:58');
INSERT INTO `member` VALUES (100004, 0, 'lee', '', 0.00, 45, 'uAf+f73qyqB4LqA2KIPcEA==', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKeoQUBJZ40FDibYOQKAYJJGXxMWZ8FehDrNZ4gYw98qwMaCyPBwDd1kbLqa1Z3mUTOdAZjchIYcLw/132', '', 0, 'opLxO5cE7MXKPxj2ndOxnvxkoek0', 1, '2020-04-15 07:35:30', '2020-03-26 13:09:20');
INSERT INTO `member` VALUES (100005, 0, '测试号小猪', '', 0.00, 0, '17717852647', '测试号', '', 0, '', '', 0, 'opLxO5QaspLK7XKWg546kYZStiYk', 1, '2020-04-08 22:12:59', '2020-04-08 22:12:59');
INSERT INTO `member` VALUES (100007, 0, '', '', 0.00, 0, '', 'ceshi', '', 0, '', '', 0, '..', 1, '2020-04-18 18:55:35', '2020-04-18 18:55:35');

-- ----------------------------
-- Table structure for member_balance_change_log
-- ----------------------------
DROP TABLE IF EXISTS `member_balance_change_log`;
CREATE TABLE `member_balance_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `unit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '变更多少',
  `total_balance` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '变更之后总量',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_balance_change_log_member_id`(`member_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员账户余额变更表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member_notify_time_change_log
-- ----------------------------
DROP TABLE IF EXISTS `member_notify_time_change_log`;
CREATE TABLE `member_notify_time_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `unit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '通知次数变更多少',
  `notify_times` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '通知次数变更之前的总量',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_notify_time_change_log_member_id`(`member_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员通知次数变更表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member_phone_change_log
-- ----------------------------
DROP TABLE IF EXISTS `member_phone_change_log`;
CREATE TABLE `member_phone_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `old_mobile` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `new_mobile` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_phone_change_log_member_id`(`member_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员手机变更表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member_sms_pkg
-- ----------------------------
DROP TABLE IF EXISTS `member_sms_pkg`;
CREATE TABLE `member_sms_pkg`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '会员id',
  `open_id` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员的openID，二维码标识',
  `left_notify_times` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '套餐剩余通知次数',
  `expired_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '消息包过期时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_sms_pkg_open_id`(`open_id`) USING BTREE,
  INDEX `ix_member_sms_pkg_expired_time`(`expired_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '短信套餐包表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member_sms_pkg_change_log
-- ----------------------------
DROP TABLE IF EXISTS `member_sms_pkg_change_log`;
CREATE TABLE `member_sms_pkg_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `pkg_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '会员的短信包id',
  `unit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '短信包余量变更多少',
  `notify_times` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '短信包内变更前的总量',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_sms_pkg_change_log_member_id`(`member_id`) USING BTREE,
  INDEX `ix_member_sms_pkg_change_log_pkg_id`(`pkg_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员短信包通知次数变更表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for member_status_change_log
-- ----------------------------
DROP TABLE IF EXISTS `member_status_change_log`;
CREATE TABLE `member_status_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `old_status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '会员旧状态 状态 1：有效 0：无效 -1:无效',
  `new_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '会员新状态 状态 1：有效 0：无效 -1:无效',
  `user_id` int(11) UNSIGNED NOT NULL COMMENT '操作的管理员id',
  `stuff_id` int(11) UNSIGNED NOT NULL COMMENT '相关的物品或答谢id',
  `stuff_type` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1：物品 2：答谢',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `member_reason` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '申诉理由',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '记录状态 0:无申诉 1:申诉 2:申诉成功 3:申诉驳回',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_member_status_change_log_member_id`(`member_id`) USING BTREE,
  INDEX `ix_member_status_change_log_stuff_id`(`stuff_id`) USING BTREE,
  INDEX `ix_member_status_change_log_stuff_type`(`stuff_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员状态变更记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for order
-- ----------------------------
DROP TABLE IF EXISTS `order`;
CREATE TABLE `order`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '随机订单号',
  `member_id` bigint(11) NOT NULL DEFAULT 0 COMMENT '会员id',
  `total_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '订单应付金额',
  `yun_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '运费金额',
  `pay_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '订单实付金额',
  `discount_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '折扣金额',
  `discount_type` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '折扣类型',
  `pay_sn` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方流水号',
  `prepay_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方预付id',
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '备注信息',
  `status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1：支付完成 0 无效 -1 申请退款 -2 退款中 -9 退款成功  -8 待支付  -7 完成支付待确认',
  `express_status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '快递状态，-8 待支付 -7 已付款待发货 1：确认收货 0：失败',
  `express_address_id` int(11) NOT NULL DEFAULT 0 COMMENT '快递地址id',
  `express_info` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '快递信息',
  `comment_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '评论状态',
  `pay_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '付款到账时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `express_sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '快递单号',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_order_sn`(`order_sn`) USING BTREE,
  INDEX `idx_order_status`(`status`) USING BTREE,
  INDEX `idx_member_id_status`(`member_id`, `status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '周边购买订单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for order_callback_data
-- ----------------------------
DROP TABLE IF EXISTS `order_callback_data`;
CREATE TABLE `order_callback_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL DEFAULT 0 COMMENT '支付订单id',
  `pay_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '支付回调信息',
  `refund_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '退款回调信息',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_order_callback_data_order_id`(`order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '微信支付回调数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for order_product
-- ----------------------------
DROP TABLE IF EXISTS `order_product`;
CREATE TABLE `order_product`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_id` int(11) UNSIGNED NOT NULL COMMENT '订单id',
  `member_id` bigint(11) NOT NULL DEFAULT 0 COMMENT '会员id',
  `product_id` int(11) UNSIGNED NOT NULL COMMENT '产品id',
  `product_num` int(11) UNSIGNED NOT NULL DEFAULT 1 COMMENT '购买数, 默认1份',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '商品总价格，售价 * 数量',
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '备注信息',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态：1：成功 0 失败',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_order_product_member_id`(`member_id`) USING BTREE,
  INDEX `ix_order_product_order_id`(`order_id`) USING BTREE,
  INDEX `ix_order_product_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '订单包含的周边表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for product
-- ----------------------------
DROP TABLE IF EXISTS `product`;
CREATE TABLE `product`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '产品id',
  `common_id` int(11) NOT NULL COMMENT '公共产品id',
  `option_id` int(11) NOT NULL COMMENT '规格id',
  `option_desc` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '规格描述',
  `cat_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '周边类别id',
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '周边名',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '单价',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '组图',
  `tags` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'tag关键字，以\',\'相连',
  `description` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '详情描述',
  `status` tinyint(1) UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态 1：有效 0：无效',
  `view_cnt` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '浏览量',
  `stock_cnt` int(11) UNSIGNED NOT NULL DEFAULT 99999 COMMENT '库存量',
  `sale_cnt` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '销售量',
  `comment_cnt` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论量',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_product_cat_id`(`cat_id`) USING BTREE,
  INDEX `ix_product_common_id`(`common_id`) USING BTREE,
  INDEX `ix_product_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '周边表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of product
-- ----------------------------
INSERT INTO `product` VALUES (1, 1, 0, '防水', 1, '稿纸', 10.00, '20200303/paper1.jpg', '20200303/paper1.jpg', '', '爱丢笔记本的TJer，快把实惠的稿纸带回家吧~', 1, 0, 99999, 0, 0, '2020-02-25 19:33:24', '2020-02-20 12:21:28');
INSERT INTO `product` VALUES (2, 2, 0, '三折伞', 2, '伞', 40.00, '20200303/umbrella1.jpg', '20200303/umbrella1.jpg', '', '独特的闪寻伞，教室门口的一把回头伞，妈妈再也不怕我雨天上学丢伞了', 1, 0, 99999, 0, 0, '2020-02-28 14:04:59', '2020-02-20 12:21:42');
INSERT INTO `product` VALUES (3, 3, 0, '圆形纯LOGO', 2, '钥匙扣', 30.00, '20200303/keyring1.jpg', '20200303/keyring1.jpg', '', '闪寻的可爱刺猬LOGO，闪寻粉丝纪念品', 1, 0, 99999, 0, 0, '2020-03-03 04:33:34', '2020-02-20 12:22:17');
INSERT INTO `product` VALUES (4, 3, 1, '圆形LOGO二维码', 2, '钥匙扣', 30.00, '20200303/keyring2.jpg', '20200303/keyring2.jpg', '', '闪寻LOGO迷你居于二维码中央，身形小巧，易于携带', 1, 0, 99999, 0, 0, '2020-02-28 14:04:59', '2020-02-20 12:22:17');
INSERT INTO `product` VALUES (5, 3, 2, '二维码附信息方卡', 2, '钥匙扣', 30.00, '20200303/keyring3.jpg', '20200303/keyring3.jpg', '', '信息卡上附带联络方式，方便捡到的人直接联系爱丢东西的你', 1, 0, 99999, 0, 0, '2020-03-03 04:33:34', '2020-02-20 12:22:17');
INSERT INTO `product` VALUES (6, 4, 0, '手账必备', 1, '胶带', 30.00, '20200303/tape1.jpg', '20200303/tape1.jpg', '', '轻松一粘，易丢物品闪寻~', 1, 0, 99999, 0, 0, '2020-02-26 12:39:37', '2020-02-26 12:39:37');
INSERT INTO `product` VALUES (7, 5, 0, 'LOGO二维码', 2, '徽章', 20.00, '20200303/badge1.jpg', '20200303/badge1.jpg', '', 'LOGO二维码', 1, 0, 99999, 0, 0, '2020-03-02 16:56:34', '2020-03-02 16:56:34');
INSERT INTO `product` VALUES (8, 5, 1, '纯LOGO', 2, '徽章', 10.00, '20200303/badge2.jpg', '20200303/badge2.jpg', '', '纯LOGO', 1, 0, 99999, 0, 0, '2020-03-02 16:56:34', '2020-03-02 16:56:34');
INSERT INTO `product` VALUES (9, 5, 2, '纯二维码', 2, '徽章', 20.00, '20200303/badge3.jpg', '20200303/badge3.jpg', '', '纯二维码', 1, 0, 99999, 0, 0, '2020-03-02 16:56:34', '2020-03-02 16:56:34');
INSERT INTO `product` VALUES (10, 5, 3, '组合', 2, '徽章', 50.00, '20200303/badge4.jpg', '20200303/badge4.jpg', '', '包含所有徽章，组合价更优惠~', 1, 0, 99999, 0, 0, '2020-03-02 16:56:34', '2020-03-02 16:56:34');
INSERT INTO `product` VALUES (11, 6, 0, '水印', 1, '印章', 50.00, '20200303/stamper1.jpg', '20200303/stamper1.jpg', '', '可以敲在书本上，你的闪寻名片', 1, 0, 99999, 0, 0, '2020-03-03 04:33:34', '2020-03-02 20:24:22');
INSERT INTO `product` VALUES (12, 6, 1, '钢印', 1, '印章', 90.00, '20200303/stamper2.jpg', '20200303/stamper2.jpg', '', '可以敲在书本上，你的闪寻名片', 1, 0, 99999, 0, 0, '2020-03-03 04:33:34', '2020-03-02 20:24:31');
INSERT INTO `product` VALUES (13, 7, 0, '加鸡腿', 2, '打赏', 0.01, '20200307/chicken1.jpg', '20200307/chicken1.jpg', '', '一分钱也是爱', 1, 0, 99987, 12, 0, '2020-04-07 00:31:38', '2020-03-07 20:24:31');
INSERT INTO `product` VALUES (14, 7, 1, '加整鸡', 2, '打赏', 0.02, '20200307/chicken2.jpg', '20200307/chicken2.jpg', '', '两分钱也是爱', 1, 0, 99999, 0, 0, '2020-03-27 11:00:52', '2020-03-07 20:24:31');
INSERT INTO `product` VALUES (15, 8, 0, '直接获码', 1, '失物贴码，拾者扫码归还。通知短信1次1毛，购买即赠5次免费通知！', 2.5, '20200321/sx-code.jpg', '20200321/sx-code.jpg', '', '有了它，失物闪寻！', 0, 0, 99999997, 3, 0, '2020-03-29 19:57:53', '2020-03-21 15:21:04');
INSERT INTO `product` VALUES (16, 9, 0, '2年50次通知包', 1, '50次3年有效期', 4.5, '20200327/sms1.jpg', '20200327/sms1.jpg', '', '有了它，懒人专用通知包', 0, 0, 99999999, 1, 0, '2020-04-01 02:56:11', '2020-03-27 12:44:12');
INSERT INTO `product` VALUES (17, 9, 1, '按量计费通知', 1, '1次失物通知，购买通知套餐包价格更优惠哦', 0.10, '20200327/sms2.jpg', '20200327/sms2.jpg', '', '有了它，失物通知即刻到', 0, 0, 999999991, 9, 0, '2020-04-01 03:39:05', '2020-03-27 12:45:20');

-- ----------------------------
-- Table structure for product_category
-- ----------------------------
DROP TABLE IF EXISTS `product_category`;
CREATE TABLE `product_category`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '类别名称',
  `weight` tinyint(4) NOT NULL DEFAULT 1 COMMENT '权重',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：有效 0：无效',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '周边分类' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of product_category
-- ----------------------------
INSERT INTO `product_category` VALUES (1, '文具', 1, 1, '2020-02-21 07:14:19', '2020-02-21 07:14:19');
INSERT INTO `product_category` VALUES (2, '生活', 1, 1, '2020-02-21 07:14:23', '2020-02-21 07:14:23');

-- ----------------------------
-- Table structure for product_comments
-- ----------------------------
DROP TABLE IF EXISTS `product_comments`;
CREATE TABLE `product_comments`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL DEFAULT 0 COMMENT '会员id',
  `product_ids` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '商品ids',
  `order_id` int(11) NOT NULL DEFAULT 0 COMMENT '订单id',
  `score` tinyint(4) NOT NULL DEFAULT 0 COMMENT '评分',
  `content` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '评论内容',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_product_comments_member_id`(`member_id`) USING BTREE,
  INDEX `ix_product_comments_order_id`(`order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员评论表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for product_sale_change_log
-- ----------------------------
DROP TABLE IF EXISTS `product_sale_change_log`;
CREATE TABLE `product_sale_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL DEFAULT 0 COMMENT '商品id',
  `quantity` int(11) NOT NULL DEFAULT 0 COMMENT '售卖数量',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '售卖金额',
  `member_id` int(11) NOT NULL DEFAULT 0 COMMENT '会员id',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '售卖时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_product_sale_change_log_product_id`(`product_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '商品销售情况' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for product_stock_change_log
-- ----------------------------
DROP TABLE IF EXISTS `product_stock_change_log`;
CREATE TABLE `product_stock_change_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL COMMENT '商品id',
  `unit` int(11) NOT NULL DEFAULT 0 COMMENT '变更多少',
  `total_stock` int(11) NOT NULL DEFAULT 0 COMMENT '变更之后总量',
  `note` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注字段',
  `created_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_product_stock_change_log_product_id`(`product_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '数据库存变更表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for recommend
-- ----------------------------
DROP TABLE IF EXISTS `recommend`;
CREATE TABLE `recommend`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `found_goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拾物id',
  `lost_goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '寻物id',
  `target_member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '看到此推荐记录的用户id',
  `rel_score` float(8, 4) UNSIGNED NOT NULL DEFAULT 1.0000 COMMENT '匹配的相似度',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '状态 0:未读, 1:已读, -1: 已删除',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_recommend_found_goods_id`(`found_goods_id`) USING BTREE,
  INDEX `ix_recommend_lost_goods_id`(`lost_goods_id`) USING BTREE,
  INDEX `ix_recommend_target_member_id`(`target_member_id`) USING BTREE,
  INDEX `ix_recommend_status`(`status`) USING BTREE,
  INDEX `ix_recommend_rel_score`(`rel_score`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '推荐表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for report
-- ----------------------------
DROP TABLE IF EXISTS `report`;
CREATE TABLE `report`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '处理举报的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '发布消息的会员id',
  `report_member_id` int(11) UNSIGNED NOT NULL COMMENT '举报消息的会员id',
  `report_member_nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '举报消息的会员名',
  `report_member_avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '举报消息的会员头像',
  `record_id` int(11) UNSIGNED NOT NULL COMMENT '信息id，有可能是物品信息违规，也可能是用户的答谢违规',
  `summary` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `record_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：物品信息违规 0：答谢信息违规',
  `deleted_by` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '删除举报的管理员id',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_report_record_id`(`record_id`) USING BTREE,
  INDEX `ix_report_status`(`status`) USING BTREE,
  INDEX `ix_report_record_type`(`record_type`) USING BTREE,
  INDEX `ix_report_deleted_by`(`deleted_by`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '举报消息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for thank_order
-- ----------------------------
DROP TABLE IF EXISTS `thank_order`;
CREATE TABLE `thank_order`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '随机订单号',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '第三方id',
  `transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '微信支付交易号',
  `price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '支付金额',
  `balance_discount` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '余额垫付金额',
  `status` tinyint(1) NOT NULL DEFAULT -1 COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付完成时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_thank_order_order_sn`(`order_sn`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '答谢支付的订单' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for thank_order_callback_data
-- ----------------------------
DROP TABLE IF EXISTS `thank_order_callback_data`;
CREATE TABLE `thank_order_callback_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thank_order_id` int(11) NOT NULL DEFAULT 0 COMMENT '支付订单id',
  `pay_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '支付回调信息',
  `refund_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '退款回调信息',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_order_callback_data_order_id`(`thank_order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '答谢微信支付回调数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for thanks
-- ----------------------------
DROP TABLE IF EXISTS `thanks`;
CREATE TABLE `thanks`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拉黑会员的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '发布感谢的会员id',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '发布感谢的会员名',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '发布感谢的会员头像',
  `order_sn` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '微信支付的订单流水号',
  `thank_price` decimal(10, 2) UNSIGNED NOT NULL DEFAULT 0.00 COMMENT '答谢总金额',
  `target_member_id` int(11) UNSIGNED NOT NULL COMMENT '接受消息的会员id',
  `goods_id` int(11) UNSIGNED NOT NULL COMMENT '物品id',
  `summary` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `goods_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物品名称',
  `business_desc` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '拾到或者丢失',
  `owner_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户的名称，可能只是微信昵称',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `report_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '被举报后的状态，用于存储举报的状态值',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_thanks_member_id`(`member_id`) USING BTREE,
  INDEX `ix_thanks_target_member_id`(`target_member_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '答谢表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `uid` int(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '注册会员id',
  `level` int(11) UNSIGNED NOT NULL COMMENT '管理员等级',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '手机号码',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '邮箱地址',
  `sex` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1：男 2：女 0：没填写',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '头像',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1：有效 0：无效',
  `op_uid` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '操作管理员id',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '管理员表' ROW_FORMAT = Dynamic;
INSERT INTO `user` VALUES (4, 100002, 1, '李依璇', '17717090831', '17702113437@163.com', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', 1, 4, '2020-04-23 15:46:54', '2020-04-23 15:46:54');
INSERT INTO `user` VALUES (5, 100001, 1, '李佩璇', '17717852647', '290036208@qq.com', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', 0, 4, '2020-05-01 13:56:51', '2020-04-24 21:08:54');

-- ----------------------------
-- Table structure for wechat_server_api_log
-- ----------------------------
DROP TABLE IF EXISTS `wechat_server_api_log`;
CREATE TABLE `wechat_server_api_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `url` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '请求地址',
  `req_data` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '请求数据',
  `resp_data` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '响应数据',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `token` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '请求令牌',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_wechat_server_api_url`(`url`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '微信服务端API调用日志' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
