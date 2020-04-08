

-- --------------------------------------------------------------------------------------------------------------
-- CASE0001 新增归还测试的数据准备
-- --------------------------------------------------------------------------------------------------------------
-- 1、U1 发布寻物贴
-- 2、U2 归还
-- 3、U1进入归还通知页
-- 4、U1查看归还贴->查看原寻物贴->查看
-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100002, 0, '管理员', '', 4.73, 70, '17717852647', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-03-31 01:56:32', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100001, 0, 'L  yx', '', 14.48, 320, '17717090831', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '20200329/ce40c3ef-2959-4a35-85a4-7f2c6b688cbe.jpg', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-04 23:34:48', '2020-03-17 20:09:58');

-- ----------------------------
-- Records of goods
-- ----------------------------
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 0, '', 1, 0, 2, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');


-- ----------------------------
-- 寻物归还后更新的goods数据
-- ----------------------------
-- 寻物归还1~4后的数据
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 3, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 2, 0, 3, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, 0, 1, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');

-- -----------------------------
-- 扫码归还后更新的goods数据
-- -----------------------------
INSERT INTO `goods` VALUES (4, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '钱包', 'TEST', '上海市杨浦区四平路1239号###同济大学(四平路校区)###31.282628###121.50183', 0.00, '20200407/cfa9c9e6aeb24323ad11595e288839f6.jpg', '20200407/cfa9c9e6aeb24323ad11595e288839f6.jpg', '测试扫码归还', 2, 'opLxO5Q3CloBEmwcarKrF_kSA574', 0, '', 2, 0, 0, '2020-04-07 17:47:37', 1, 0, 1, '2020-04-07 17:47:38', '2020-04-07 17:47:38');



-- --------------------------------------------------------------------------------------------------------------
-- CASE0002 删除归还的测试数据准备
-- --------------------------------------------------------------------------------------------------------------
-- 寻物归还：U1 操作
-- 1.1、U1 进入归还通知，进入详情否认（对方进入归还详情可见，对方已拒绝，去公开；我的帖子待归还）
-- 1.2、U1 进入归还通知，待确认页，批量删除（对方进入归还详情可见，对方已拒绝，去公开；我的帖子待归还）
--------------NONONONONO 1.2.2、U1 进入归还通知，待取回页、批量确认
-- 1.3.1、U1 进入归还通知，已取回页、批量删除（询问是否删除寻物帖子，记录归还日志，解除人的链接关系）
-- 1.3.2、U1 进入归还通知，已答谢页、批量删除（询问是否删除寻物帖子，记录归还日志后，解除双方链接关系）
-- 1.4.1、U1 进入发布记录，预寻回页，批量删除（只删自己，对方进入归还详情，可见原帖子已删，去公开）
-- 1.4.2、U1 进入发布记录，已寻回页、批量删除（只删自己，对方进入归还详情，可见原帖子已删）
-- 1.4.3、U1 进入归还通知，已答谢页、批量删除（只删自己，对方进入归还详情，可见原帖子已删）
-- 寻物归还：U2 操作
-- r2.1.1、U2 （进入发布记录，还->待确认页，进入详情）查看寻物详情，进行取消，选择直接删帖（只删自己，解除对方链接，对方帖子变回待归还）
-- r2.1.2、U2 （进入发布记录，还->待确认页，进入详情），查看寻物详情，进行取消，选择公开（解除双方链接，转成刚发的新失物招领，对方帖子变回待归还）
-- r2.2.1/2、U2 进入发布记录，还->待确认页，批量删除(2.1.1~2的批量操作)
-- 扫码归还：U1操作 == 寻物归还：U1操作 1.1~1.3
-- 扫码归还：U2操作 == 寻物归还：

-- 归还的时候需要订阅，归还状态通知（确认/否认）

-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100002, 0, '管理员', '', 4.73, 70, '17717852647', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-03-31 01:56:32', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100001, 0, 'L  yx', '', 14.48, 320, '17717090831', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '20200329/ce40c3ef-2959-4a35-85a4-7f2c6b688cbe.jpg', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-04 23:34:48', '2020-03-17 20:09:58');
-- ----------------------------
-- Records of goods（寻物归还用）
-- ----------------------------
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 3, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 2, 0, 6, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, 0, 6, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');
-- ----------------------------
-- Records of goods（扫码归还用）
-- ----------------------------
INSERT INTO `goods` VALUES (4, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '钱包', 'TEST', '上海市杨浦区四平路1239号###同济大学(四平路校区)###31.282628###121.50183', 0.00, '20200407/cfa9c9e6aeb24323ad11595e288839f6.jpg', '20200407/cfa9c9e6aeb24323ad11595e288839f6.jpg', '测试扫码归还', 2, 'opLxO5Q3CloBEmwcarKrF_kSA574', 0, '', 2, 0, 0, '2020-04-07 17:47:37', 1, 0, 1, '2020-04-07 17:47:38', '2020-04-07 17:47:38');

-- ----------------------------
-- 1.1、1.2 后更新的goods数据
-- ----------------------------
-- 被归还者单个和批量拒绝（对方进入归还详情可见，对方已拒绝，去公开）
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 0, '', 1, 0, 8, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 0, '', 0, 0, 8, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');

-- ----------------------------
-- 2.1.1、2.2.1 后更新的goods数据
-- ----------------------------
--  归还者取消，选择直接删帖（只删自己，解除对方链接，对方帖子变回待归还）
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 0, '', 1, 0, 8, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, 'opLxO5Q3CloBEmwcarKrF_kSA574', 7, 0, 7, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 22:46:09', '2020-04-07 15:28:47');

-- ----------------------------
-- 2.1.2、2.2.2 后更新的goods数据
-- ----------------------------
-- 归还者选择公开（解除双方链接，转成刚发的新失物招领，对方帖子变回待归还）
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 0, '', 1, 0, 6, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 1, '', 0, '', 1, 0, 7, '2020-04-07 23:55:05', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');

-- ------------------------
-- 被归还者取回后的goods数据
-- -----------------------
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 3, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 3, 0, 7, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 100002, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, 'opLxO5Q3CloBEmwcarKrF_kSA574', 3, 0, 8, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');

-- ---------------------------
-- 被归还者删除已取回后的goods数据
-- --------------------------
-- 删除已取回时，智能删除了链接的寻物贴
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 3, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 7, 0, 6, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 100002, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, '', 3, 0, 6, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');

-- ---------------------------------------
-- 归还者基于前面仅删除自己的归还贴goods数据
-- --------------------------------------
INSERT INTO `goods` VALUES (1, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '20200407/fe6987dc3ccf4454aab089578aaca7f8.png', '测试归还\n测试匹配', 0, '', 3, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 7, 0, 9, '2020-04-07 15:13:08', 3, 0, 1, '2020-04-07 15:13:09', '2020-04-07 15:13:09');
INSERT INTO `goods` VALUES (3, 0, 100001, 'opLxO5fubMUl7GdPFgZOUaDHUik8', '管理员', 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '高危非必填', 100002, '校园卡', 'TEST', '上海市上海市徐汇区凌云路###梅陇十村(上海市徐汇区凌云路)###31.13233###121.4229', 0.00, '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '20200407/050fb4dfe1194e2982ec83aa8edf1328.jpg', '测试发布归还贴', 2, '', 1, '', 7, 0, 13, '2020-04-07 15:28:47', 3, 0, 1, '2020-04-07 15:28:47', '2020-04-07 15:28:47');




-- --------------------------------------------------------------------------------------------------------------
-- CASE0003 测试认领数据准备
-- --------------------------------------------------------------------------------------------------------------
-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100001, 0, '管理员', '', 4.73, 70, '17717852647', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-03-31 01:56:32', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100002, 0, 'L  yx', '', 14.48, 320, '17717090831', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '20200329/ce40c3ef-2959-4a35-85a4-7f2c6b688cbe.jpg', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-04 23:34:48', '2020-03-17 20:09:58');

-- ----------------------------
-- Records of goods
-- ----------------------------
INSERT INTO `goods` VALUES (2, 0, 100002, 'opLxO5Q3CloBEmwcarKrF_kSA574', 'L  yx', 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '高危非必填', 0, '快递', 'TEST2', '上海市上海市闵行区莲花路2251号###虹桥派出所###31.175468###121.38918', 0.00, '20200407/976ebaa20177464c882b7e12817efecd.jpg', '20200407/976ebaa20177464c882b7e12817efecd.jpg', '测试认领', 1, '', 0, '', 1, 0, 1, '2020-04-07 15:17:45', 8, 0, 1, '2020-04-07 15:17:46', '2020-04-07 15:17:46');

-- ----------------------------
-- Records of mark after mark
-- ----------------------------

-- ----------------------------
-- Records of goods after mark
-- ----------------------------





-- --------------------------------------------------------------------------------------------------------------
-- CASE0003 测试匹配数据准备
-- --------------------------------------------------------------------------------------------------------------

-- ----------------------------
-- Records of member
-- ----------------------------
INSERT INTO `member` VALUES (100001, 0, '管理员', '', 4.73, 70, '17717852647', '李佩璇', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132', '20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg', 0, 'opLxO5fubMUl7GdPFgZOUaDHUik8', 1, '2020-03-31 01:56:32', '2020-03-08 09:31:56');
INSERT INTO `member` VALUES (100002, 0, 'L  yx', '', 14.48, 320, '17717090831', 'LYX', '', 2, 'https://wx.qlogo.cn/mmopen/vi_32/SV42VibIREXs9x9LsPerNKSmtID351W69g7SAzfoWXYqbvBiaJtcPyUp4yAnedJlyWuiamGTnDAibdo4I4ibeiaeQaug/132', '20200329/ce40c3ef-2959-4a35-85a4-7f2c6b688cbe.jpg', 26, 'opLxO5Q3CloBEmwcarKrF_kSA574', 1, '2020-04-04 23:34:48', '2020-03-17 20:09:58');


