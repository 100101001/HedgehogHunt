/*
 Navicat Premium Data Transfer

 Source Server         : opencs
 Source Server Type    : MySQL
 Source Server Version : 50727
 Source Host           : 47.102.201.193:3306
 Source Schema         : ciwei_db

 Target Server Type    : MySQL
 Target Server Version : 50727
 File Encoding         : 65001

 Date: 27/03/2020 12:47:59
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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

SET FOREIGN_KEY_CHECKS = 1;
