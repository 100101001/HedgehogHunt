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

 Date: 27/03/2020 12:36:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for qr_code
-- ----------------------------
DROP TABLE IF EXISTS `qr_code`;
CREATE TABLE `qr_code`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `member_id` int(11) UNSIGNED NOT NULL COMMENT '会员id',
  `openid` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '第三方id',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `order_id` int(11) UNSIGNED NULL DEFAULT NULL COMMENT '微信支付的订单id',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员姓名',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '会员收货地址',
  `qr_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '二维码图片',
  `updated_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_qr_code_openid`(`openid`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '二维码表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of qr_code
-- ----------------------------
INSERT INTO `qr_code` VALUES (1, 100000, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200308/55fa270a-f740-4e12-a885-c93d6f96e877.jpg', '2020-03-08 09:28:04', '2020-03-08 09:28:04');
INSERT INTO `qr_code` VALUES (2, 100002, 'opLxO5fmwgdzntX4gfdKEk5NqLQA', '18385537403', NULL, '韦朝旭', '', '20200308/c8322bb0-92d7-482f-b237-fc95bb18b490.jpg', '2020-03-08 12:44:15', '2020-03-08 12:44:15');
INSERT INTO `qr_code` VALUES (3, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '17717852647', NULL, '李佩璇', '', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', '2020-03-16 19:14:00', '2020-03-16 19:14:00');
INSERT INTO `qr_code` VALUES (4, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200317/23ab1cda-7d2f-4ece-9b7a-6008521e7cdb.jpg', '2020-03-17 22:26:15', '2020-03-17 22:26:15');
INSERT INTO `qr_code` VALUES (5, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/161b3685-a99b-4375-b361-dd0d4c1dde90.jpg', '2020-03-21 12:05:39', '2020-03-21 12:05:39');
INSERT INTO `qr_code` VALUES (6, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/9ed8edc6-8284-4c33-8214-ec44e4b626a8.jpg', '2020-03-21 17:47:39', '2020-03-21 17:47:39');
INSERT INTO `qr_code` VALUES (7, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/d9205897-fa32-45f0-9b5a-e0f59e1d8f5c.jpg', '2020-03-21 18:09:47', '2020-03-21 18:09:47');
INSERT INTO `qr_code` VALUES (8, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/9541e3c5-bea5-4628-92e8-f9d7b72616d2.jpg', '2020-03-21 18:31:34', '2020-03-21 18:31:34');
INSERT INTO `qr_code` VALUES (9, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/922dcf5d-9cfe-45ce-850f-b4bfa44ec6d9.jpg', '2020-03-21 19:35:28', '2020-03-21 19:35:28');
INSERT INTO `qr_code` VALUES (10, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/76e62c07-fd0b-41bd-bff8-300c1f3e6f80.jpg', '2020-03-21 19:39:50', '2020-03-21 19:39:50');
INSERT INTO `qr_code` VALUES (11, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/3fcef9d1-02cf-4c7d-a305-6803e27011c3.jpg', '2020-03-21 19:41:39', '2020-03-21 19:41:39');
INSERT INTO `qr_code` VALUES (12, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/d96474e7-a47f-4e8f-82df-3ebe17f4fc6e.jpg', '2020-03-21 19:50:41', '2020-03-21 19:50:41');
INSERT INTO `qr_code` VALUES (13, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/b57505d4-efa9-47dc-a6a9-1d0ff65ea312.jpg', '2020-03-21 20:09:39', '2020-03-21 20:09:39');
INSERT INTO `qr_code` VALUES (14, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/33e0c108-c246-4f90-9eaf-7807ea143081.jpg', '2020-03-21 20:18:02', '2020-03-21 20:18:02');
INSERT INTO `qr_code` VALUES (15, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/b3eb4e91-2852-47d9-80cb-35fb8b602e4c.jpg', '2020-03-21 20:22:07', '2020-03-21 20:22:07');
INSERT INTO `qr_code` VALUES (16, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/afcd91c7-8276-4208-ab4c-62dabdec33e2.jpg', '2020-03-21 20:24:09', '2020-03-21 20:24:09');
INSERT INTO `qr_code` VALUES (17, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/9d1369e4-7827-4a6e-bce2-6d37ced436cc.jpg', '2020-03-21 21:20:11', '2020-03-21 21:20:11');
INSERT INTO `qr_code` VALUES (18, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/7458ba08-f287-4a5e-bc8a-56a11fcdb1d2.jpg', '2020-03-21 21:23:42', '2020-03-21 21:23:42');
INSERT INTO `qr_code` VALUES (19, 100007, 'opLxO5Q3CloBEmwcarKrF_kSA574', '17717090831', NULL, '李依璇', '', '20200321/84bf6054-6e42-4ac1-babd-b7aeeba9dcb8.jpg', '2020-03-25 19:27:16', '2020-03-21 21:41:48');
INSERT INTO `qr_code` VALUES (20, 100017, 'opLxO5cE7MXKPxj2ndOxnvxkoek0', '18964779230', NULL, '李佩璇', '', '20200326/6bbaf16e-7d19-4b41-af30-5394c7491dd0.jpg', '2020-03-26 13:09:42', '2020-03-26 13:09:42');

SET FOREIGN_KEY_CHECKS = 1;
