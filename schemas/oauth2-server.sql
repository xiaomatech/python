CREATE TABLE IF NOT EXISTS clients (
  id BINARY(8) PRIMARY KEY,
  hashed_secret BINARY(32),
  hashed_secret_previous BINARY(32),
  name VARCHAR(256) NOT NULL,
  image_uri VARCHAR(256) NOT NULL,
  redirect_uri VARCHAR(256) NOT NULL,
  can_grant BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trusted BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS codes (
  code BINARY(32) PRIMARY KEY,
  client_id BINARY(8) NOT NULL,
  INDEX codes_client_id(client_id),
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
  userId BIGINT(20) NOT NULL,
  INDEX codes_user_id(userId),
  email VARCHAR(256) NOT NULL,
  scope VARCHAR(256) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  auth_at BIGINT DEFAULT 0,
  offline BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS tokens (
  token BINARY(32) PRIMARY KEY,
  client_id BINARY(8) NOT NULL,
  INDEX tokens_client_id(client_id),
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
  user_id BIGINT(20) NOT NULL,
  INDEX tokens_user_id(user_id),
  email VARCHAR(256) NOT NULL,
  type VARCHAR(16) NOT NULL,
  scope VARCHAR(256) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  INDEX idx_expiresAt(expires_at)
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS developers (
  developer_id BIGINT(20) NOT NULL,
  client_id BINARY(8) NOT NULL,
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS clientDevelopers (
  row_id BINARY(8) PRIMARY KEY,
  developer_id BIGINT(20) NOT NULL,
  client_id BINARY(8) NOT NULL,
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS refreshTokens (
  token BINARY(32) PRIMARY KEY,
  client_id BINARY(8) NOT NULL,
  INDEX tokens_client_id(client_id),
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
  user_id BIGINT(20) NOT NULL,
  INDEX tokens_user_id(user_id),
  email VARCHAR(256) NOT NULL,
  scope VARCHAR(256) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;
