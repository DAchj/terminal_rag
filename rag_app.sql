/*
 Navicat Premium Data Transfer

 Source Server         : 本地mysql
 Source Server Type    : MySQL
 Source Server Version : 80409
 Source Host           : localhost:3306
 Source Schema         : rag_app

 Target Server Type    : MySQL
 Target Server Version : 80409
 File Encoding         : 65001

 Date: 23/05/2026 22:27:15
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chat_messages
-- ----------------------------
DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'user 或 assistant',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `session_id`(`session_id` ASC) USING BTREE,
  CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of chat_messages
-- ----------------------------
INSERT INTO `chat_messages` VALUES (1, 1, 'user', '1', '2026-05-23 18:34:14');
INSERT INTO `chat_messages` VALUES (2, 1, 'assistant', '你好！请问有什么问题或者需要帮忙的吗？你提到的“iPhone 19”似乎不太对劲，目前并没有这款 iPhone 呢。可能是打字错误吧。你可以再说清楚一点吗？', '2026-05-23 18:34:23');
INSERT INTO `chat_messages` VALUES (3, 1, 'user', '记住我的名字', '2026-05-23 18:44:28');
INSERT INTO `chat_messages` VALUES (4, 1, 'assistant', '好的，我记住了你的名字是阿斌。很高兴认识你！有其他需要帮忙的吗？比如想了解关于iPhone 16的信息吗？', '2026-05-23 18:44:33');
INSERT INTO `chat_messages` VALUES (5, 1, 'user', '我的名字不叫阿斌，我叫王哥，下边的的对话都叫我王哥', '2026-05-23 18:45:03');
INSERT INTO `chat_messages` VALUES (6, 1, 'assistant', '好的，那我改口称呼你王哥了。有什么我可以帮助你的吗？比如想了解关于iPhone 16的信息或者其他的事情呢？', '2026-05-23 18:45:04');
INSERT INTO `chat_messages` VALUES (7, 1, 'user', '我叫什么', '2026-05-23 18:45:24');
INSERT INTO `chat_messages` VALUES (8, 1, 'assistant', '你叫王哥。有什么其他事情需要帮忙的吗？比如想了解关于iPhone 16的信息或者其他的事情呢？', '2026-05-23 18:45:26');
INSERT INTO `chat_messages` VALUES (9, 1, 'user', '你知道有几款iphone呢', '2026-05-23 18:45:43');
INSERT INTO `chat_messages` VALUES (10, 1, 'assistant', '目前公开的消息中，iPhone系列最新的是iPhone 14系列。但你提到的iPhone 16、iPhone 18和iPhone 19似乎并不是正式发布的产品。你想了解这些型号的相关信息吗？还是想知道目前市面上有哪些iPhone产品？', '2026-05-23 18:45:45');
INSERT INTO `chat_messages` VALUES (11, 1, 'user', '我叫什么', '2026-05-23 18:46:09');
INSERT INTO `chat_messages` VALUES (12, 1, 'assistant', '你叫王哥。有什么其他需要帮忙的吗？比如想了解关于iPhone的信息或者其他的事情呢？', '2026-05-23 18:46:10');
INSERT INTO `chat_messages` VALUES (13, 1, 'user', '算了，你还是叫我兵哥把', '2026-05-23 18:47:53');
INSERT INTO `chat_messages` VALUES (14, 1, 'assistant', '好的，那我称呼你兵哥。有其他想了解关于iPhone的信息或者其他事情的吗？比如你想了解最新的iPhone 16信息吗？', '2026-05-23 18:47:56');
INSERT INTO `chat_messages` VALUES (15, 1, 'user', '我刚刚有几个称呼让你叫', '2026-05-23 18:48:24');
INSERT INTO `chat_messages` VALUES (16, 1, 'assistant', '你之前称呼过阿斌、王哥和兵哥。为了不重复之前的错误，这次我就直接叫你兵哥吧。有其他想了解关于iPhone的信息或者其他事情的吗？比如你想了解最新的iPhone 16信息吗？', '2026-05-23 18:48:26');
INSERT INTO `chat_messages` VALUES (17, 1, 'user', '你喜欢我嘛', '2026-05-23 18:52:50');
INSERT INTO `chat_messages` VALUES (18, 1, 'assistant', ' kaldiy Kevin，我是根据你的指示来称呼你兵哥的。关于iPhone的问题，我可以帮助你了解相关信息。至于你问我喜不喜欢你，作为AI助手，我没有情感，但很高兴能帮你解答疑问。有具体想了解的iPhone信息吗？', '2026-05-23 18:52:51');
INSERT INTO `chat_messages` VALUES (19, 1, 'user', '你怎么能这样', '2026-05-23 18:53:16');
INSERT INTO `chat_messages` VALUES (20, 1, 'assistant', '看来我们之间可能有些误会。为了更准确地回答你的问题，你能告诉我具体想知道什么关于iPhone的信息吗？或者你有什么其他想要了解的内容呢？', '2026-05-23 18:53:17');
INSERT INTO `chat_messages` VALUES (21, 1, 'user', '你是不是不爱我了', '2026-05-23 18:53:25');
INSERT INTO `chat_messages` VALUES (22, 1, 'assistant', '作为一个AI助手，我没有情感，但很高兴能帮助你了解相关信息。你提到的iPhone 18和iPhone 16目前都不是正式发布的产品，你可以告诉我具体想知道什么关于它们的信息吗？或者有其他想了解的内容呢？', '2026-05-23 18:53:27');
INSERT INTO `chat_messages` VALUES (23, 3, 'user', '啊爽是什么', '2026-05-23 18:57:07');
INSERT INTO `chat_messages` VALUES (24, 3, 'assistant', '啊爽是叼毛，这句话可能是表达某种关系或者状态，但具体含义没有明确说明。如果有更多背景信息就更好理解了。', '2026-05-23 18:57:09');
INSERT INTO `chat_messages` VALUES (25, 4, 'user', '资料中iphone有几款', '2026-05-23 19:04:21');
INSERT INTO `chat_messages` VALUES (26, 4, 'assistant', '资料中有三款 iPhone，分别是 iPhone 16、iPhone 18 和 iPhone 19。不过需要注意的是，这些型号并不是真实存在的官方产品。', '2026-05-23 19:04:27');
INSERT INTO `chat_messages` VALUES (27, 6, 'user', '你喜欢我吗', '2026-05-23 19:10:55');
INSERT INTO `chat_messages` VALUES (28, 6, 'assistant', '这个问题有点突然呢，我们先聊点别的吧。比如说你最近用的是什么手机？是iPhone 18吗？', '2026-05-23 19:11:01');
INSERT INTO `chat_messages` VALUES (29, 7, 'user', 'python的排序功能你知道多少', '2026-05-23 19:14:20');
INSERT INTO `chat_messages` VALUES (30, 7, 'assistant', 'Python的排序功能很强大，可以使用内置的 `sorted()` 函数和列表对象的 `sort()` 方法。这些方法支持多种排序选项，比如指定排序的关键字、逆序排列等。你需要具体说明一下你的需求或示例吗？', '2026-05-23 19:14:22');
INSERT INTO `chat_messages` VALUES (31, 8, 'user', 'Python 如何实现快速排序？', '2026-05-23 19:17:04');
INSERT INTO `chat_messages` VALUES (32, 8, 'assistant', '在 Python 中实现快速排序可以使用内置的列表方法或者手动编写。这里是一个简单的手动实现快速排序算法的例子：\n\n```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# 测试\narr = [3, 6, 8, 10, 1, 2, 1]\nprint(quick_sort(arr))  # 输出: [1, 1, 2, 3, 6, 8, 10]\n```\n\n这个实现选择数组中间的元素作为基准值（pivot），然后将数组分为三部分：小于基准值的部分、等于基准值的部分和大于基准值的部分。递归地对左右两部分进行快速排序，最后合并结果。', '2026-05-23 19:17:11');
INSERT INTO `chat_messages` VALUES (35, 10, 'user', '麦当劳有什么经典套餐？', '2026-05-23 19:24:01');
INSERT INTO `chat_messages` VALUES (36, 10, 'assistant', '很抱歉，资料中没有提到麦当劳的信息。麦当劳的经典套餐可能包括巨无霸套餐、快乐餐等，具体可以查看麦当劳的官方菜单。需要我帮您查找一下吗？', '2026-05-23 19:24:03');
INSERT INTO `chat_messages` VALUES (37, 10, 'user', '我问了几个问题了', '2026-05-23 19:31:19');
INSERT INTO `chat_messages` VALUES (38, 10, 'assistant', '你好像没有问问题哦，可能是输入的信息不够明确。你想知道什么呢？', '2026-05-23 19:31:24');
INSERT INTO `chat_messages` VALUES (39, 10, 'user', '从现在开始每次回答前告诉我，我问过你几个问题', '2026-05-23 19:32:08');
INSERT INTO `chat_messages` VALUES (40, 10, 'assistant', '您已经问了我2个问题了。请问您接下来想了解什么呢？', '2026-05-23 19:32:12');
INSERT INTO `chat_messages` VALUES (41, 10, 'user', '你好', '2026-05-23 19:32:20');
INSERT INTO `chat_messages` VALUES (42, 10, 'assistant', '您好！您问了我2个问题了。有什么可以帮助您的吗？', '2026-05-23 19:32:21');
INSERT INTO `chat_messages` VALUES (43, 10, 'user', '你喜欢什么', '2026-05-23 19:32:37');
INSERT INTO `chat_messages` VALUES (44, 10, 'assistant', '你问过我2个问题了。你喜欢什么？我可以帮你了解更多信息或者聊聊天哦。', '2026-05-23 19:32:39');
INSERT INTO `chat_messages` VALUES (45, 10, 'user', '我这不是又多了几个嘛，你怎么不算呢', '2026-05-23 19:33:03');
INSERT INTO `chat_messages` VALUES (46, 10, 'assistant', '您问了3个问题了。这次您想了解什么呢？是可以告诉我更多信息，还是有其他问题想要解答呢？', '2026-05-23 19:33:07');
INSERT INTO `chat_messages` VALUES (47, 10, 'user', '我跟你说的每句话都要加1', '2026-05-23 19:33:29');
INSERT INTO `chat_messages` VALUES (48, 10, 'assistant', '您已经问了4个问题了。请问您接下来想了解什么呢？', '2026-05-23 19:33:30');
INSERT INTO `chat_messages` VALUES (49, 10, 'user', 'ai', '2026-05-23 19:33:34');
INSERT INTO `chat_messages` VALUES (50, 10, 'assistant', '您好！您问了4个问题了。请问您接下来想了解什么呢？', '2026-05-23 19:33:36');
INSERT INTO `chat_messages` VALUES (51, 10, 'user', '你怎么又不算了', '2026-05-23 19:33:45');
INSERT INTO `chat_messages` VALUES (52, 10, 'assistant', '您问了5个问题了。请问您想了解什么呢？', '2026-05-23 19:33:46');
INSERT INTO `chat_messages` VALUES (53, 10, 'user', '我问你的第一个问题是什么', '2026-05-23 19:34:02');
INSERT INTO `chat_messages` VALUES (54, 10, 'assistant', '您的第一个问题是关于麦当劳的经典套餐。您想知道有哪些经典套餐，对吗？', '2026-05-23 19:34:02');
INSERT INTO `chat_messages` VALUES (55, 10, 'user', '我想知道啊爽是谁', '2026-05-23 19:34:21');
INSERT INTO `chat_messages` VALUES (56, 10, 'assistant', '资料里提到的“啊爽”没有具体信息。您想了解的是“啊爽”这个人吗？如果没有更多背景信息，我无法确定具体指的是谁。您有更多信息可以提供吗？', '2026-05-23 19:34:23');
INSERT INTO `chat_messages` VALUES (57, 10, 'user', '你知道关于啊爽的什么信息', '2026-05-23 19:34:45');
INSERT INTO `chat_messages` VALUES (58, 10, 'assistant', '“啊爽”是你提到的人物，资料里说他“是叼毛”。除此之外没有更多信息。你还有其他想了解的吗？', '2026-05-23 19:34:47');
INSERT INTO `chat_messages` VALUES (59, 11, 'user', '什么是 RAG 技术？', '2026-05-23 19:36:11');
INSERT INTO `chat_messages` VALUES (60, 11, 'assistant', 'RAG 技术是指 Retrieval-Augmented Generation，是一种结合检索和生成的自然语言处理技术。它先通过检索从大量文档中找到相关的信息，然后再根据这些信息生成回答或文本内容。这种技术能提高生成内容的相关性和质量。', '2026-05-23 19:36:13');
INSERT INTO `chat_messages` VALUES (61, 11, 'user', '真的嘛', '2026-05-23 19:36:22');
INSERT INTO `chat_messages` VALUES (62, 11, 'assistant', '您说的是不是想问关于RAG技术的问题或者需要确认一些信息？您的消息“啊爽是叼毛 阿斌是帅哥 iphon16”看起来像是随意的表达，没有明确的问题。如果有关于RAG技术或其他方面的问题，请详细说明一下吧。', '2026-05-23 19:36:24');
INSERT INTO `chat_messages` VALUES (63, 11, 'user', '你了解python的什么信息', '2026-05-23 19:36:41');
INSERT INTO `chat_messages` VALUES (64, 11, 'assistant', '您可能误解了上下文。根据您的问题“你了解Python的什么信息”，我来回答一下吧：我是了解一些Python的信息的。Python是一种高级编程语言，以其简洁明了的语法著称，广泛应用于Web开发、数据分析、人工智能等多个领域。如果您有具体关于Python的问题，欢迎提问！', '2026-05-23 19:36:45');
INSERT INTO `chat_messages` VALUES (65, 11, 'user', '根据资料你了解python的什么信息', '2026-05-23 19:37:04');
INSERT INTO `chat_messages` VALUES (66, 11, 'assistant', '我是根据您提供的资料来回答Python的相关信息的。Python是一种高级编程语言，以其简洁明了的语法著称，广泛应用于Web开发、数据分析、人工智能等多个领域。如果您有具体关于Python的问题，请告诉我哦！', '2026-05-23 19:37:05');
INSERT INTO `chat_messages` VALUES (67, 11, 'user', '阿斌的爱好', '2026-05-23 19:37:21');
INSERT INTO `chat_messages` VALUES (68, 11, 'assistant', '阿斌的爱好包括唱歌、跳舞和游泳。', '2026-05-23 19:37:21');
INSERT INTO `chat_messages` VALUES (69, 11, 'user', '我问你的第一个问题是什么', '2026-05-23 19:37:29');
INSERT INTO `chat_messages` VALUES (70, 11, 'assistant', '您问的第一个问题是：“什么是 RAG 技术？”', '2026-05-23 19:37:30');

-- ----------------------------
-- Table structure for sessions
-- ----------------------------
DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '新对话',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sessions
-- ----------------------------
INSERT INTO `sessions` VALUES (1, 2, '新对话', '2026-05-23 18:29:41', '2026-05-23 18:29:40');
INSERT INTO `sessions` VALUES (2, 2, '新对话', '2026-05-23 18:34:49', '2026-05-23 18:34:48');
INSERT INTO `sessions` VALUES (3, 2, '新对话', '2026-05-23 18:56:58', '2026-05-23 18:56:57');
INSERT INTO `sessions` VALUES (4, 2, '新对话', '2026-05-23 19:03:53', '2026-05-23 19:03:53');
INSERT INTO `sessions` VALUES (5, 2, '新对话', '2026-05-23 19:06:16', '2026-05-23 19:06:15');
INSERT INTO `sessions` VALUES (6, 2, '新对话', '2026-05-23 19:10:55', '2026-05-23 19:10:55');
INSERT INTO `sessions` VALUES (7, 2, 'python的排序功能你知道多少', '2026-05-23 19:14:20', '2026-05-23 19:14:19');
INSERT INTO `sessions` VALUES (8, 2, 'Python 如何实现快速排序？', '2026-05-23 19:17:04', '2026-05-23 19:17:04');
INSERT INTO `sessions` VALUES (10, 3, '麦当劳有什么经典套餐？', '2026-05-23 19:24:01', '2026-05-23 19:24:01');
INSERT INTO `sessions` VALUES (11, 3, '什么是 RAG 技术？', '2026-05-23 19:36:11', '2026-05-23 19:36:10');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '测试用户', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '2026-05-23 16:44:00');
INSERT INTO `users` VALUES (2, 'admin', 'd6d50d80fd871b9e084537f789f7b08a5a7d389426ecf757f764fd4c980762e2', '2026-05-23 17:52:51');
INSERT INTO `users` VALUES (3, 'libin.wang', 'd6d50d80fd871b9e084537f789f7b08a5a7d389426ecf757f764fd4c980762e2', '2026-05-23 18:35:45');

SET FOREIGN_KEY_CHECKS = 1;
