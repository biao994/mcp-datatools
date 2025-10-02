-- data/init_scripts/postgresql.sql
-- PostgreSQL测试数据库初始化

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO users (name, email) VALUES 
    ('吴邪', 'wuxie@example.com'),
    ('张起灵', 'zhangqiling@example.com'),
    ('王胖子', 'wangpangzi@example.com');

INSERT INTO products (name, price, category) VALUES 
    ('洛阳铲', 299.99, '探测工具'),
    ('夜明珠', 9999.99, '照明装备'),
    ('黑驴蹄子', 88.88, '防护用品'),
    ('金刚伞', 1299.99, '防御装备');

INSERT INTO orders (user_id, total_amount, status) VALUES 
    (1, 10299.98, 'completed'),   -- 吴邪：夜明珠+洛阳铲
    (2, 88.88, 'pending'),        -- 张起灵：黑驴蹄子
    (3, 1388.87, 'shipped');      -- 王胖子：金刚伞+黑驴蹄子

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
```

```sql
-- data/init_scripts/mysql.sql
-- MySQL测试数据库初始化

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 插入测试数据
INSERT INTO users (name, email) VALUES 
    ('胡八一', 'hubayii@example.com'),
    ('王凯旋', 'wangkaixuan@example.com'),
    ('雪莉杨', 'xueliyang@example.com');

INSERT INTO products (name, price, category) VALUES 
    ('摸金符', 888.88, '护身符'),
    ('金刚伞', 1588.88, '防御装备'),
    ('黑驴蹄子', 66.66, '镇邪用品'),
    ('探照灯', 299.99, '照明装备');

INSERT INTO orders (user_id, total_amount, status) VALUES 
    (1, 955.54, 'completed'),    -- 胡八一：摸金符+黑驴蹄子
    (2, 299.99, 'pending'),      -- 王凯旋：探照灯
    (3, 1655.54, 'shipped');     -- 雪莉杨：金刚伞+黑驴蹄子

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);