CREATE TABLE `user` (
  `user_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int NOT NULL DEFAULT '0',
  `create_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `exec_status` int unsigned NOT NULL DEFAULT '0',
  `api_status` int unsigned NOT NULL DEFAULT '0',
  UNIQUE KEY `user_UN` (`user_id`),
  KEY `user_status_IDX` (`status`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='user'