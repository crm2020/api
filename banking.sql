/*
 Navicat Premium Data Transfer

 Source Server         : banking
 Source Server Type    : MySQL
 Source Server Version : 80400 (8.4.0)
 Source Host           : 145.24.223.91:3306
 Source Schema         : banking

 Target Server Type    : MySQL
 Target Server Version : 80400 (8.4.0)
 File Encoding         : 65001

 Date: 29/05/2024 00:54:26
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for Account
-- ----------------------------
DROP TABLE IF EXISTS `Account`;
CREATE TABLE `Account`  (
  `IBAN` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `FirstName` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `LastName` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `Email` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `BirthDate` date NULL DEFAULT NULL,
  `Balance` int NULL DEFAULT NULL,
  PRIMARY KEY (`IBAN`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of Account
-- ----------------------------
INSERT INTO `Account` VALUES ('NL91NSBA0417164300', 'John', 'Doe', 'john.doe@example.com', '1980-01-01', 1000);

-- ----------------------------
-- Table structure for Cards
-- ----------------------------
DROP TABLE IF EXISTS `Cards`;
CREATE TABLE `Cards`  (
  `CardID` int NOT NULL AUTO_INCREMENT,
  `CardNR` int NULL DEFAULT NULL,
  `ExpDate` date NULL DEFAULT NULL,
  `Blocked` int NULL DEFAULT NULL,
  `Account_IBAN` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `AttemptsRemaining` int NOT NULL DEFAULT 3,
  PRIMARY KEY (`CardID`) USING BTREE,
  INDEX `Account_IBAN`(`Account_IBAN` ASC) USING BTREE,
  CONSTRAINT `Cards_ibfk_1` FOREIGN KEY (`Account_IBAN`) REFERENCES `Account` (`IBAN`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of Cards
-- ----------------------------
INSERT INTO `Cards` VALUES (1, 1234, '2025-01-01', 0, 'NL91NSBA0417164300', 3);

-- ----------------------------
-- Table structure for Pincodes
-- ----------------------------
DROP TABLE IF EXISTS `Pincodes`;
CREATE TABLE `Pincodes`  (
  `PinID` int NOT NULL AUTO_INCREMENT,
  `PinCode` int NULL DEFAULT NULL,
  `CardID` int NULL DEFAULT NULL,
  PRIMARY KEY (`PinID`) USING BTREE,
  INDEX `CardID`(`CardID` ASC) USING BTREE,
  CONSTRAINT `Pincodes_ibfk_1` FOREIGN KEY (`CardID`) REFERENCES `Cards` (`CardID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of Pincodes
-- ----------------------------
INSERT INTO `Pincodes` VALUES (1, 1234, 1);

-- ----------------------------
-- Table structure for Transactions
-- ----------------------------
DROP TABLE IF EXISTS `Transactions`;
CREATE TABLE `Transactions`  (
  `ID` int NOT NULL,
  `Date` date NULL DEFAULT NULL,
  `Amount` int NULL DEFAULT NULL,
  `Account_IBAN` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`ID`) USING BTREE,
  INDEX `Account_IBAN`(`Account_IBAN` ASC) USING BTREE,
  CONSTRAINT `Transactions_ibfk_1` FOREIGN KEY (`Account_IBAN`) REFERENCES `Account` (`IBAN`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of Transactions
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
