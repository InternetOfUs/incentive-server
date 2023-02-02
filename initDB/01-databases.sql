# create databases
CREATE DATABASE IF NOT EXISTS `lassi`;
CREATE DATABASE IF NOT EXISTS `libraries`;

# create root user and grant rights
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';