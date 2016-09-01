CREATE TABLE `user_oauth` (
  `oauth_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `oauth` enum('qq','wechat','weibo') NOT NULL DEFAULT 'qq' COMMENT '第三方站名',
  `oauth_openid` varchar(100) NOT NULL COMMENT '第三方openid',
  `oauth_username` varchar(100) NOT NULL COMMENT '第三方用户名',
  `oauth_avatar` varchar(100) NOT NULL COMMENT '第三方头像',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`oauth_id`),
  UNIQUE KEY `user_id_oauth` (`user_id`,`oauth`),
  KEY `oauth_id_user_id` (`user_id`,`oauth_openid`)
) ENGINE=InnoDB;


CREATE TABLE `users` (
  `user_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `user_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户名',
  `user_email` varchar(255) NOT NULL COMMENT '邮箱',
  `user_status` enum('new','delete','ban','day_active','week_active','month_active') NOT NULL DEFAULT 'new' COMMENT '用户状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `logged_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后登陆时间',
  `user_phone` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '手机号',
  PRIMARY KEY (`user_id`),
  KEY `user_phone` (`user_phone`),
  KEY `user_status` (`user_status`)
) ENGINE=InnoDB;