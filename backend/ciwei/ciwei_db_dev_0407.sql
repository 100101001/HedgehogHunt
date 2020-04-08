/*
 Navicat Premium Data Transfer

 Source Server         : ciwei-root2
 Source Server Type    : MySQL
 Source Server Version : 50729
 Source Host           : 192.168.0.116:3306
 Source Schema         : ciwei_db2

 Target Server Type    : MySQL
 Target Server Version : 50729
 File Encoding         : 65001

 Date: 03/03/2020 15:09:46
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '大学表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of campus
-- ----------------------------
INSERT INTO `campus` VALUES (1, '同济大学', 'TJ', 'TJU.jpeg', '2020-02-20 12:20:29', '2020-02-20 12:20:29');
-- INSERT INTO `campus` VALUES (2, '北京大学', 'PKU', 'PKU.jpeg', '2020-02-20 12:20:41', '2020-02-20 12:20:41');
-- INSERT INTO `campus` VALUES (3, '北京师范', 'BNU', 'BNU.jpeg', '2020-02-24 18:22:16', '2020-02-24 18:22:16');
-- INSERT INTO `campus` VALUES (4, '东南大学', 'SEU', 'SEU.jpg', '2020-02-24 18:22:35', '2020-02-24 18:22:35');
-- INSERT INTO `campus` VALUES (5, '西安交大', 'XJTU', 'XJTU.jpeg', '2020-02-24 18:22:55', '2020-02-24 18:22:55');
-- INSERT INTO `campus` VALUES (6, '四川大学', 'SCU', 'SCU.jpeg', '2020-02-24 18:23:11', '2020-02-24 18:23:11');

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
) ENGINE = InnoDB AUTO_INCREMENT = 27 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '大学周边表' ROW_FORMAT = Dynamic;

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
-- INSERT INTO `campus_product` VALUES (7, 2, 4, '2020-02-26 12:39:11', '2020-02-26 12:39:11');
-- INSERT INTO `campus_product` VALUES (8, 3, 1, '2020-02-28 06:03:14', '2020-02-28 06:03:14');
-- INSERT INTO `campus_product` VALUES (9, 3, 2, '2020-02-28 06:03:18', '2020-02-28 06:03:18');
-- INSERT INTO `campus_product` VALUES (10, 3, 4, '2020-02-28 06:03:25', '2020-02-28 06:03:25');
-- INSERT INTO `campus_product` VALUES (11, 4, 1, '2020-02-28 06:03:30', '2020-02-28 06:03:30');
-- INSERT INTO `campus_product` VALUES (12, 4, 4, '2020-02-28 06:03:34', '2020-02-28 06:03:34');
-- INSERT INTO `campus_product` VALUES (13, 4, 3, '2020-02-28 06:03:38', '2020-02-28 06:03:38');
-- INSERT INTO `campus_product` VALUES (14, 5, 2, '2020-02-28 06:03:43', '2020-02-28 06:03:43');
-- INSERT INTO `campus_product` VALUES (15, 5, 3, '2020-02-28 06:03:47', '2020-02-28 06:03:47');
-- INSERT INTO `campus_product` VALUES (16, 5, 4, '2020-02-28 06:03:51', '2020-02-28 06:03:51');
-- INSERT INTO `campus_product` VALUES (17, 6, 1, '2020-02-28 06:03:55', '2020-02-28 06:03:55');
-- INSERT INTO `campus_product` VALUES (18, 6, 2, '2020-02-28 06:03:59', '2020-02-28 06:03:59');
-- INSERT INTO `campus_product` VALUES (19, 6, 3, '2020-02-28 06:04:02', '2020-02-28 06:04:02');
-- INSERT INTO `campus_product` VALUES (20, 6, 4, '2020-02-28 06:04:06', '2020-02-28 06:04:06');
-- INSERT INTO `campus_product` VALUES (21, 2, 1, '2020-02-20 12:23:02', '2020-02-20 12:23:02');
-- INSERT INTO `campus_product` VALUES (22, 2, 2, '2020-02-20 12:23:05', '2020-02-20 12:23:05');
-- INSERT INTO `campus_product` VALUES (23, 2, 3, '2020-02-20 12:23:09', '2020-02-20 12:23:09');
-- INSERT INTO `campus_product` VALUES (24, 2, 5, '2020-03-02 22:48:29', '2020-03-02 22:48:29');
-- INSERT INTO `campus_product` VALUES (25, 2, 4, '2020-03-02 22:48:38', '2020-03-02 22:48:38');
-- INSERT INTO `campus_product` VALUES (26, 3, 4, '2020-03-02 22:48:43', '2020-03-02 22:48:43');

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
  `uu_id` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '唯一标识',
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '处理反馈消息的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '反馈消息的会员id',
  `summary` varchar(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '组图',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE
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
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物品放置地址',
  `target_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '悬赏金额',
  `main_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '主图',
  `pics` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '组图',
  `summary` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `business_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：失物招领 0：寻物启事',
  `qr_code_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '扫码归还的码主的openid',
  `return_goods_id` int(11) UNSIGNED DEFAULT 0  COMMENT '归还的寻物启示ID',
  `return_goods_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '归还的寻物启示OPENID',
  `status` tinyint(1) UNSIGNED NOT NULL DEFAULT 7 COMMENT '1:待, 2:预, 3:已, 5:管理员删, 7:发布者创建中, 8:发布者被管理员拉黑',
  `is_thanked` tinyint(1) NOT NULL DEFAULT 0 COMMENT '状态 0：未答谢 1:已答谢',
  `view_count` int(11) NOT NULL DEFAULT 0 COMMENT '总浏览次数',
  `top_expire_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '置顶过期时间',
  `category` tinyint(1) UNSIGNED NOT NULL DEFAULT 10 COMMENT '1:钱包 2：钥匙 3: 卡类/证照 4: 数码产品 5：手袋/挎包 6：衣服/鞋帽 7：首饰/挂饰 8：行李/包裹 9：书籍/文件 10：其它',
  `recommended_times` int(11) NOT NULL DEFAULT 0 COMMENT '总匹配过失/拾物次数',
  `report_status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '被举报后的状态，用于存储举报的状态值',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_goods_member_id`(`member_id`) USING BTREE,
  INDEX `ix_goods_status`(`status`) USING BTREE,
  INDEX `ix_goods_top_expire_time`(`top_expire_time`) USING BTREE,
  INDEX `ix_goods_view_count`(`view_count`) USING BTREE,
  INDEX `ix_goods_category`(`category`) USING BTREE,
  INDEX `ix_goods_owner_id`(`owner_id`) USING BTREE,
  INDEX `ix_goods_qr_code_openid`(`qr_code_openid`) USING BTREE,
  INDEX `ix_goods_return_goods_openid`(`return_goods_openid`) USING BTREE,
  INDEX `ix_goods_business_type`(`business_type`) USING BTREE,
  INDEX `ix_goods_is_thanked`(`is_thanked`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1  CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品表' ROW_FORMAT = Dynamic;


-- ----------------------------------
-- Table structure for goods_category
-- ----------------------------
DROP TABLE IF EXISTS `goods_category`;
CREATE TABLE `goods_category`  (
   `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
   `tag` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '类别标签',
   `default_goods` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '类别默认失物',
   PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1  CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品类别表' ROW_FORMAT = Dynamic;
INSERT INTO `goods_category` VALUES (1,'钱包','钱包');
INSERT INTO `goods_category` VALUES (2,'钥匙', '钥匙');
INSERT INTO `goods_category` VALUES (3,'卡类/证照', '校园卡');
INSERT INTO `goods_category` VALUES (4,'数码产品', '手机');
INSERT INTO `goods_category` VALUES (5,'手袋/挎包', '书包');
INSERT INTO `goods_category` VALUES (6,'衣服/鞋帽', '外套');
INSERT INTO `goods_category` VALUES (7,'首饰/挂饰', '手链');
INSERT INTO `goods_category` VALUES (8,'行李/包裹', '快递');
INSERT INTO `goods_category` VALUES (9,'书籍/文件', '文件夹');
INSERT INTO `goods_category` VALUES (10,'其它', '');


-- ----------------------------
-- Table structure for recommend
-- ----------------------------
DROP TABLE IF EXISTS `recommend`;
CREATE TABLE `recommend`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `found_goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拾物id',
  `lost_goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '寻物id',
  `target_member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '看到此推荐记录的用户id',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '状态 0:未读, 1:已读, -1: 已删除',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_recommend_found_goods_id`(`found_goods_id`) USING BTREE,
  INDEX `ix_recommend_lost_goods_id`(`lost_goods_id`) USING BTREE,
  INDEX `ix_recommend_target_member_id`(`target_member_id`) USING BTREE,
  INDEX `ix_recommend_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '推荐表' ROW_FORMAT = Dynamic;


-- ----------------------------
-- Table structure for mark
-- ----------------------------
DROP TABLE IF EXISTS `mark`;
CREATE TABLE `mark`(
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '认领的物品id',
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '用户id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 0:未取 1:已取',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_mark_member_id`(`member_id`) USING BTREE,
  INDEX `ix_mark_goods_id`(`goods_id`) USING BTREE,
  INDEX `ix_mark_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '认领表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for appeal
-- ----------------------------
DROP TABLE IF EXISTS `appeal`;
CREATE TABLE `appeal`(
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `goods_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '申诉的物品id',
  `member_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '用户id',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 0:待处理 1:已处理完毕',
  `adm_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '系统指派处理的管理员id',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_appeal_member_id`(`member_id`) USING BTREE,
  INDEX `ix_appeal_goods_id`(`goods_id`) USING BTREE,
  INDEX `ix_appeal_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '申诉表' ROW_FORMAT = Dynamic;

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
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
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
) ENGINE = InnoDB AUTO_INCREMENT = 100000 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员表' ROW_FORMAT = Dynamic;

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
  `express_sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '快递单号',
  `comment_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '评论状态',
  `pay_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '付款到账时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_order_sn`(`order_sn`) USING BTREE,
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
) ENGINE = InnoDB AUTO_INCREMENT =1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '订单包含的周边表' ROW_FORMAT = Dynamic;

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
  `sale_cnt` int(11) NOT NULL DEFAULT 0 COMMENT '销售量',
  `comment_cnt` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论量',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_product_cat_id`(`cat_id`) USING BTREE
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
INSERT INTO `product` VALUES (13, 7, 0, '加鸡腿', 2, '打赏', 0.01, '20200307/chicken1.jpg', '20200307/chicken1.jpg', '', '一分钱也是爱', 1, 0, 99997, 1, 0, '2020-03-27 11:02:54', '2020-03-07 20:24:31');
INSERT INTO `product` VALUES (14, 7, 1, '加整鸡', 2, '打赏', 0.02, '20200307/chicken2.jpg', '20200307/chicken2.jpg', '', '两分钱也是爱', 1, 0, 99999, 0, 0, '2020-03-27 11:00:52', '2020-03-07 20:24:31');
INSERT INTO `product` VALUES (15, 8, 0, '直接获码', 1, '失物贴码，拾者扫码归还。通知短信1次1毛，购买即赠5次免费通知！', 2.50, '20200321/sx-code.jpg', '20200321/sx-code.jpg', '', '有了它，失物闪寻！', 0, 0, 100000000, 0, 0, '2020-03-21 15:21:04', '2020-03-21 15:21:04');
INSERT INTO `product` VALUES (16, 9, 0, '2年50次通知包', 1, '50次3年有效期', 4.50, '20200327/sms1.jpg', '20200327/sms1.jpg', '', '有了它，懒人专用通知包', 0, 0, 100000000, 0, 0, '2020-03-27 12:44:12', '2020-03-27 12:44:12');
INSERT INTO `product` VALUES (17, 9, 1, '按量计费通知', 1, '1次失物通知，购买通知套餐包价格更优惠哦', 0.10, '20200327/sms2.jpg', '20200327/sms2.jpg', '', '有了它，失物通知即刻到', 0, 0, 1000000000, 0, 0, '2020-03-27 12:45:20', '2020-03-27 12:45:20');

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
  UNIQUE INDEX `idx_product_category_name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '周边分类' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of product_cat
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
-- Table structure for product_option
-- ----------------------------
DROP TABLE IF EXISTS `product_option`;
CREATE TABLE `product_option`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `product_id` int(11) UNSIGNED NOT NULL,
  `option_id` int(11) UNSIGNED NOT NULL,
  `summary` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1：有效 0：无效',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_product_option_product_id`(`product_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '周边规格表' ROW_FORMAT = Dynamic;

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
-- Table structure for member_sms_pkg
-- ----------------------------
DROP TABLE IF EXISTS `member_sms_pkg`;
CREATE TABLE `member_sms_pkg`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
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
-- Table structure for queue_list
-- ----------------------------
DROP TABLE IF EXISTS `queue_list`;
CREATE TABLE `queue_list`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '队列名字',
  `data` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '队列数据',
  `status` tinyint(1) NOT NULL DEFAULT -1 COMMENT '状态 -1 待处理 1 已处理',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '事件队列表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for report
-- ----------------------------
DROP TABLE IF EXISTS `report`;
CREATE TABLE `report`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '拉黑会员的管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '发布消息的会员id',
  `report_member_id` int(11) UNSIGNED NOT NULL COMMENT '举报消息的会员id',
  `record_id` int(11) NOT NULL COMMENT '信息id，有可能是物品信息违规，也可能是用户的答谢违规',
  `summary` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `record_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：物品信息违规 0：答谢信息违规',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE
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
  `status` tinyint(1) NOT NULL DEFAULT -1 COMMENT '状态 -1=刚创建, 0=微信预下单-未支付,  1=微信支付成功, 2=微信已关单, 3=微信支付错误',
  `paid_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付完成时间',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_thank_order_order_sn`(`order_sn`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '答谢支付的订单' ROW_FORMAT = Dynamic;

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
  `goods_id` int(11) NOT NULL COMMENT '物品id',
  `summary` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '描述',
  `goods_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '物品名称',
  `business_desc` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '拾到或者丢失',
  `owner_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户的名称，可能只是微信昵称',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1：已读 0：未读',
  `report_status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '被举报后的状态，用于存储举报的状态值',
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
  `uid` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '管理员id',
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '注册会员id',
  `level` int(11) UNSIGNED NOT NULL COMMENT '管理员等级',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '手机号码',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '邮箱地址',
  `sex` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1：男 2：女 0：没填写',
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '头像',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1：有效 0：无效',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '管理员表' ROW_FORMAT = Dynamic;

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
  UNIQUE INDEX `ix_goods_top_order_callback_data_order_id`(`top_order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品置顶微信支付回调数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for acs_sms_send_log
-- ----------------------------
DROP TABLE IF EXISTS `acs_sms_send_log`;
CREATE TABLE `acs_sms_send_log`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `biz_uuid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '本地业务ID',
  `phone_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '手机号',
  `sign_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '阿里云签名名称',
  `template_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '阿里云模板id',
  `params` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模板消息参数',
  `acs_product_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '阿里云产品名',
  `acs_resp_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用相应数据体',
  `acs_request_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用请求ID',
  `acs_biz_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用业务ID',
  `acs_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调用结果代码',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_acs_sms_send_log_uuid`(`biz_uuid`) USING BTREE,
  INDEX `ix_acs_sms_send_log_tmp_id`(`template_id`) USING BTREE COMMENT '模板ID，区分是否是验证码短信',
  INDEX `ix_acs_sms_send_log_phone_number`(`phone_numer`) USING BTREE COMMENT '手机号'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '阿里云服务短信发送调用日志' ROW_FORMAT = Dynamic;


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


SET FOREIGN_KEY_CHECKS = 1;