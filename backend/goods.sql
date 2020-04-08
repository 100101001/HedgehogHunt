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

 Date: 07/04/2020 15:20:16
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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
  `qr_code_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '扫码归还的码主的openid',
  `return_goods_id` int(11) UNSIGNED NULL DEFAULT 0 COMMENT '归还的寻物启示ID',
  `return_goods_openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '归还的寻物启示OPENID',
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
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '物品表' ROW_FORMAT = Dynamic;


SET FOREIGN_KEY_CHECKS = 1;
