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

 Date: 05/04/2020 16:05:22
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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
) ENGINE = InnoDB AUTO_INCREMENT = 100046 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100001, 0, '管理员', '', 4.73, 70, '17717852647', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-03-31 01:56:32', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100002, 0, 'Joker', '', 0.95, 0, '18385537403', '韦朝旭', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/bIp2ka72wPydCEsH6U1oFbVoINfxeJwJ4uGTicGfgSCGC8jGPCnicxAIPlCt2bkUy50cCPEbOPo4cm39r6seyLVw/132', '20200328/c7d0b4f6-107b-486f-bdce-7809dabe16fa.jpg', 0, 'opLxO5fmwgdzntX4gfdKEk5NqLQA', 1, '2020-03-28 14:43:25', '2020-03-08 12:40:39');
INSERT INTO `member` VALUES (100003, 0, '娟木子', '', 0.00, 0, '13026135563', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/jjiaSefoDyb4BhlJSQHFSialxWeBLQes9U985cNCEXrbcicBNXYQQibYORTevFJUskHg0TSbWt0nbBIOwDBGrJT6YA/132', '', 0, 'opLxO5dC1tNcruIyk7CoyewWFEGk', 1, '2020-03-16 22:52:58', '2020-03-16 22:52:58');
INSERT INTO `member` VALUES (100004, 0, '刘琴Qin Liu', '', 5.00, 0, '18621897079', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/DYAIOgq83eqE4KhIM2hU3rxwelA3qldhm5ph0icYsDZ5HHnWmMaqOXkZNugMZTQ6O9RuLLMEEtzUDRy9d6siauicw/132', '', 0, 'opLxO5elkQO0LPbBHiRpRQGeIHF8', 1, '2020-03-17 18:57:41', '2020-03-17 11:24:43');
INSERT INTO `member` VALUES (100007, 0, 'L  yx', '', 14.48, 320, '17717090831', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '20200329/ce40c3ef-2959-4a35-85a4-7f2c6b688cbe.jpg', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-04 23:34:48', '2020-03-17 20:09:58');
INSERT INTO `member` VALUES (100008, 0, 'july', '', 0.00, 0, '18308640849', '', '', 0, '', '', 0, 'opLxO5RPsLDaroucCuHBgLeUkUgQ', 1, '2020-03-17 20:47:17', '2020-03-17 20:47:17');
INSERT INTO `member` VALUES (100009, 0, 'Hoxie', '', 0.00, 0, '17621478829', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJ53U73hGx22PEzqOPbW8h6e2ps7GJfIr45iaGer4LU6RxAoWh7ur4D0dicS9sOLnBOEFZ5lUHAojpQ/132', '', 0, 'opLxO5SCOYoIbSilK5l8QP6kZWck', 1, '2020-03-17 21:52:40', '2020-03-17 21:50:12');
INSERT INTO `member` VALUES (100010, 0, '🍪', '', 0.00, 0, '17878847526', '', '', 0, 'https://wx.qlogo.cn/mmopen/vi_32/azxKbHxwBOot68RqbS7T9CiapAoV9icibbLR5ia8ibzQftGbPjXtk8jAxthMDicJWNic2Lhww2mrhN1Nvtxyp5zOmHCRQ/132', '', 0, 'opLxO5bQIVj_6aOoG-vdtT79vYbE', 1, '2020-03-20 17:12:47', '2020-03-20 17:12:13');
INSERT INTO `member` VALUES (100011, 0, '中孚－马奇奇', '', 0.00, 0, '15285674196', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/NGagvQkWd8AGTnlrRK3EDe9d64vvyUicFrbOwcP6e4Vp0bC2e69oWJYD5xseibPSKYAhRmI0H7SwP90jdoNOZmEw/132', '', 0, 'opLxO5R9FbYb3tYOkD51gb-MWoLs', 1, '2020-03-23 07:35:22', '2020-03-23 07:35:22');
INSERT INTO `member` VALUES (100012, 0, '不停', '', 0.00, 5, '15705967065', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJNpx0kOlv2XCOLVIB1qaYRYohdjtdaqaIg03t4Tib1Key9Xw2ggx52LGcibVgV3rlzRuGpicoXsK0PA/132', '', 0, 'opLxO5euhNsyZfrOW9DHLesyj5UQ', 1, '2020-03-24 00:12:59', '2020-03-23 23:37:09');
INSERT INTO `member` VALUES (100013, 0, ' a\'ゞ三楼', '', 0.00, 0, '16608601091', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/bT9G8q8yblrEqLIoqaZic3QANqwibRNE8B6rTMsr5GOJwTyNt3LmicaQBc7g4S7eWSJLY9dr9z7xiaTmpptNLFqy5g/132', '', 0, 'opLxO5V2FNv8AUsylDlf3YHwYh7U', 1, '2020-03-25 07:41:11', '2020-03-25 07:41:11');
INSERT INTO `member` VALUES (100014, 0, '或许。', '', 0.00, 0, '18829335879', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTI2oBGV4iaKesUhQuxDzVibpibt7ic94G4W8ocKB1AiaVKczOyaITMg9Kag3g81oPwVrpumsrNob5xFBDw/132', '', 0, 'opLxO5WSlh2eb0-UQ5IxuaqsfZlI', 1, '2020-03-25 11:47:21', '2020-03-25 11:47:21');
INSERT INTO `member` VALUES (100015, 0, 'TForest🐧', '', 0.00, 0, '16621092360', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJjhxyb8XS28zZGowvawNicc0ES8vwOuiavfEicua0HumZFlQKHfU8Sm5Onccjp8DHh0D38DtdTiaWGRQ/132', '', 0, 'opLxO5bw0nIF02ArRrbAW-b4cNms', 1, '2020-03-25 16:37:19', '2020-03-25 16:37:19');
INSERT INTO `member` VALUES (100016, 0, '😈', '', 0.00, 0, '13643779405', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/ceHMaibqQR3crLBTv5RsrnRF8tciblhx8wH9z2pDC7L3D7uINiaKdRhqUuZSIhjXmQoIfRfuDLBTRdEsZ720oogQg/132', '', 0, 'opLxO5fhKqlntCInGMEXUIf57Zgc', 1, '2020-03-26 09:42:35', '2020-03-26 09:42:35');
INSERT INTO `member` VALUES (100017, 0, 'lee', '', 0.00, 0, '18964779230', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKeoQUBJZ40FDibYOQKAYJJGXxMWZ8FehDrNZ4gYw98qwMaCyPBwDd1kbLqa1Z3mUTOdAZjchIYcLw/132', '20200326/6bbaf16e-7d19-4b41-af30-5394c7491dd0.jpg', 0, 'opLxO5cE7MXKPxj2ndOxnvxkoek0', 1, '2020-03-26 13:09:51', '2020-03-26 13:09:20');
INSERT INTO `member` VALUES (100018, 0, '永恒', '', 0.00, 0, '13359705219', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/95Xn9fWfu9mPwokVRJpicuzCX4yhZHCSUK2Tl4zcjx8hHiabbLwNK3aPH2bhtYFIkQqznZHRfHkkeFpxHpsjaviag/132', '', 0, 'opLxO5Rd32J_nKydurcruyhuxeH0', 1, '2020-03-26 17:15:54', '2020-03-26 17:15:54');
INSERT INTO `member` VALUES (100019, 0, '@忆', '', 0.00, 0, '15127790243', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/PiajxSqBRaEI8VmaKEtXBnJ3ziaSt5Zufiaiab4u6YEh4nT8iaDsyjH9IUWhgpHBkljXz8HHeC1uzA9VB4WxNsaCHKA/132', '', 0, 'opLxO5a70lZxSW1CfDd6_lKXDQIA', 1, '2020-03-26 19:33:39', '2020-03-26 19:33:39');
INSERT INTO `member` VALUES (100020, 0, 'schumi', '', 0.00, 0, '13817390251', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTL6btb7kVwkvbYhbG71M3sL8T6pos9mzic0ssQkMQ8Qw8jmepsucpcmwhWiaT4ArPQ5F5oCP2K0V3PA/132', '', 0, 'opLxO5dq_n1xS2Uyn3zNix4mkQJY', 1, '2020-03-28 12:32:10', '2020-03-28 12:32:10');
INSERT INTO `member` VALUES (100021, 0, '空白', '', 0.00, 0, '18788605986', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/XLyJE3Byiapo2uNicH9xCe51vmulfKzu3QZnsUciadiaJSyVkt2xP02fASyudrxa9ibLzwiabVaSibPRZTyQiaztLRxeBA/132', '', 0, 'opLxO5QD0CH_qccKMpTJnAOw28Jw', 1, '2020-03-28 15:16:29', '2020-03-28 15:16:29');
INSERT INTO `member` VALUES (100033, 0, '洪涛', '', 0.00, 0, '19979061457', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/QUoXQrKHjRoCChyaBDbyHe3xP1BWCLSwBmmJWW3ia6jlbb7O45GbxeDIgKdQQeoYAs6tyw6EWiaezDcP7ubogGkg/132', '', 0, 'opLxO5QRfIs108vECfXf6jgXDWlc', 1, '2020-03-29 16:09:35', '2020-03-29 16:09:35');
INSERT INTO `member` VALUES (100034, 0, '背着居居去学习~', '', 0.00, 0, '15824948457', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTIE86Yxd95G4gNY3m0gG7wghk8ic8pyEls1dCtTeibX1gkWvYnBYJc6rN1ibicexnhV0kS5AFwbojOuNQ/132', '', 0, 'opLxO5aXWqOFETVYiyVInmhMkvW0', 1, '2020-03-30 02:28:22', '2020-03-30 02:28:22');
INSERT INTO `member` VALUES (100039, 0, '徽琂', '', 0.00, 0, '18743012352', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/UPgnHic84945Fo0Gtj2JvwicjicoRnIeMRjN1dn3tWaQXmCwbiavoiceYc8V33tCTfBicp4FSkWf5NJvmZBWOFHlYjzg/132', '', 0, 'opLxO5VfTzRtBdDPc4VlhMAs3Rdg', 1, '2020-03-31 16:23:30', '2020-03-31 16:23:30');
INSERT INTO `member` VALUES (100040, 0, '小何', '', 0.00, 0, '15986248377', '', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/DYAIOgq83eopOC8CtNOUESt7PibticfjHaPicJImaZib6KS61QwcW9ia6on77gRKQzDaUy3mBhnmiaIzGxcm0nUJ2Xhw/132', '', 0, 'opLxO5VCC7ZOr63ve9MfbT4x8LEM', 1, '2020-04-01 14:09:34', '2020-04-01 14:09:34');
INSERT INTO `member` VALUES (100041, 0, '睿和智方科技韦', '', 0.00, 0, '18932033858', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKxu6TyMBhVsjwRiapCtlaJIN7RG7p1j2kXOcvokXSDaDcKuZYiblicicVmZicLCZ08ZyROPGvibHa4tLNA/132', '', 0, 'opLxO5R1b_wolkFUZa70PbfgjG54', 1, '2020-04-02 08:28:42', '2020-04-02 08:28:42');
INSERT INTO `member` VALUES (100042, 0, '诚然', '', 0.00, 0, '18170873590', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/DYAIOgq83epmiaqyW05s8Kh9MoeodicpRenK39Q8dDwW3E6MOYkOtX8wUdegnzgbINuYqibe66oLDd5Tr4F2vAScg/132', '', 0, 'opLxO5Y_qDObJv0QXnUjwFsMvMSQ', 1, '2020-04-02 10:56:07', '2020-04-02 10:56:07');
INSERT INTO `member` VALUES (100043, 0, '乐意', '', 0.00, 0, '19959812370', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKufqV0lwn918sictbAtAedctdaPUgiadnGzmQeDjAZDaaoTwibUd3MLEw1WgV4x7iaZdM4CfJOkHMC4A/132', '', 0, 'opLxO5Z3fDvACZh07gGsr6VJewuY', 1, '2020-04-02 22:44:10', '2020-04-02 22:44:10');
INSERT INTO `member` VALUES (100044, 0, 'Hi丶boy', '', 0.00, 0, '13631145661', '', '', 1, 'https://wx.qlogo.cn/mmopen/vi_32/DYAIOgq83ep8qKk4MTicDt1vDzdEz7LKmrFU564Vb6tEwe4s0NNvxT5YWv5FYxdefKpaYrBY5iaKh3XibtFfcjaMA/132', '', 0, 'opLxO5RgM0cZl_Wgp2Lk2B542D7M', 1, '2020-04-03 00:45:15', '2020-04-03 00:45:15');
INSERT INTO `member` VALUES (100045, 0, 'Ustinian', '', 0.00, 0, '15683875969', '', '', 0, 'https://wx.qlogo.cn/mmopen/vi_32/UMj5nctf83IJsib0zTL5ZTgOQWgNFUjiccuvErZoLwFjutQiaa2zSGKGaq0DgZm4yIlgvicEn0tH7gicb8YW2MN8pgg/132', '', 0, 'opLxO5VXZtCE2YniJMIkWfB7ptk0', 1, '2020-04-04 22:35:29', '2020-04-04 22:35:29');

SET FOREIGN_KEY_CHECKS = 1;
