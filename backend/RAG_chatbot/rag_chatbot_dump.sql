-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: rag_chatbot
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `conversations`
--

DROP TABLE IF EXISTS `conversations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_conversations_user_id` (`user_id`),
  KEY `ix_conversations_id` (`id`),
  CONSTRAINT `conversations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversations`
--

LOCK TABLES `conversations` WRITE;
/*!40000 ALTER TABLE `conversations` DISABLE KEYS */;
INSERT INTO `conversations` VALUES (1,1,'hello','2025-09-25 19:36:07',NULL),(2,1,'hello','2025-09-26 10:02:42',NULL),(3,1,'hrllo','2025-09-26 10:07:35',NULL),(4,1,'hello','2025-09-26 10:13:06',NULL),(5,1,'hello','2025-09-26 10:15:56',NULL),(6,1,'hello','2025-09-26 10:16:21',NULL),(7,1,'hi','2025-09-26 10:16:59',NULL),(8,1,'hello','2025-09-26 10:25:34',NULL),(9,1,'hello','2025-09-26 10:28:44',NULL),(10,1,'hello','2025-09-26 10:30:56',NULL),(11,1,'hello','2025-09-26 10:38:40',NULL),(12,1,'hello','2025-09-26 10:40:50',NULL),(13,1,'hello','2025-09-26 10:43:23',NULL),(14,1,'hello','2025-09-26 10:43:43',NULL),(15,1,'hello','2025-09-26 10:46:17',NULL),(16,1,'hello','2025-09-26 10:48:13',NULL),(17,1,'hello','2025-09-26 10:53:07',NULL),(18,1,'hello','2025-09-26 10:57:47',NULL),(19,1,'hello','2025-09-26 11:03:16',NULL),(20,1,'hello','2025-09-26 11:13:16',NULL);
/*!40000 ALTER TABLE `conversations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `document_chunks`
--

DROP TABLE IF EXISTS `document_chunks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_chunks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `chunk_text` text NOT NULL,
  `chunk_index` int NOT NULL,
  `embedding` json DEFAULT NULL,
  `doc_metadata` json DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_document_chunks_id` (`id`),
  KEY `ix_document_chunks_document_id` (`document_id`),
  CONSTRAINT `document_chunks_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_chunks`
--

LOCK TABLES `document_chunks` WRITE;
/*!40000 ALTER TABLE `document_chunks` DISABLE KEYS */;
INSERT INTO `document_chunks` VALUES (1,2,'fastapi>=0.104.0,<0.105.0\nuvicorn[standard]>=0.24.0,<0.25.0\npydantic>=2.4.0,<3.0.0\npython-multipart>=0.0.6\npython-dotenv>=1.0.0\nsqlalchemy>=2.0.0,<3.0.0\npsycopg2-binary>=2.9.7\nalembic>=1.12.0\nrequests>=2.31.0\nhttpx>=0.25.0',0,'[-0.024537106975913048, -0.024885956197977063, -0.043960314244031906, -0.01865941286087036, -0.01252504251897335, -0.15157271921634674, -0.05952814221382141, -0.012313207611441612, -0.07696281373500824, -0.035510823130607605, -0.0112017085775733, -0.09857230633497238, -0.052535220980644226, 0.010470961220562458, 0.09372685104608536, 0.0020450809970498085, 0.022605739533901215, -0.02759484015405178, 0.02298607863485813, 0.01826062984764576, -0.031958457082509995, -0.005953273735940456, 0.06723450124263763, -0.019187312573194504, -0.03554804250597954, -0.04355432093143463, -0.043302737176418304, 0.05562055855989456, -0.007338272873312235, -0.07731358706951141, 0.02106786146759987, 0.045814596116542816, -0.08028596639633179, -0.028360482305288315, 0.1300663948059082, 0.06339975446462631, 0.0050612823106348515, -0.11672867089509964, 0.01183001883327961, 0.048627130687236786, 0.03547874093055725, -0.027143223211169243, -0.07994011789560318, -0.011261334642767906, -0.10639480501413344, -0.04765670374035835, -0.03959128260612488, 0.06903001666069031, 0.055075690150260925, -0.054387375712394714]',NULL,'2025-09-26 10:16:45');
/*!40000 ALTER TABLE `document_chunks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_size` int NOT NULL,
  `file_type` varchar(10) NOT NULL,
  `processing_status` varchar(20) DEFAULT NULL,
  `document_type` varchar(20) DEFAULT NULL,
  `extracted_text` text,
  `doc_metadata` json DEFAULT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_documents_id` (`id`),
  KEY `ix_documents_user_id` (`user_id`),
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (1,'1_0a71ce00953d980e5090cd493a066343.png','Screenshot 2025-09-25 210311.png','C:\\Users\\vrajr\\Downloads\\ai-rag-chatbot-python\\ai-rag-chatbot-python\\backend\\uploads\\1\\1_0a71ce00953d980e5090cd493a066343.png',380667,'png','failed','image',NULL,NULL,1,'2025-09-26 10:16:37','2025-09-26 10:16:37'),(2,'1_0bfa6444204b09df5028d4c14b64c61e.txt','requirements.txt','C:\\Users\\vrajr\\Downloads\\ai-rag-chatbot-python\\ai-rag-chatbot-python\\backend\\uploads\\1\\1_0bfa6444204b09df5028d4c14b64c61e.txt',222,'txt','completed','text','fastapi>=0.104.0,<0.105.0\nuvicorn[standard]>=0.24.0,<0.25.0\npydantic>=2.4.0,<3.0.0\npython-multipart>=0.0.6\npython-dotenv>=1.0.0\nsqlalchemy>=2.0.0,<3.0.0\npsycopg2-binary>=2.9.7\nalembic>=1.12.0\nrequests>=2.31.0\nhttpx>=0.25.0',NULL,1,'2025-09-26 10:16:45','2025-09-26 10:16:45');
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `conversation_id` int NOT NULL,
  `role` varchar(10) NOT NULL,
  `content` text NOT NULL,
  `sources` json DEFAULT NULL,
  `relevance_score` float DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_messages_id` (`id`),
  KEY `ix_messages_conversation_id` (`conversation_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,1,'user','hello',NULL,NULL,'2025-09-25 19:36:07'),(2,1,'assistant','Hello there! How can I help you today?\n','null',NULL,'2025-09-25 19:36:08'),(3,1,'user','how are you ??',NULL,NULL,'2025-09-25 19:36:35'),(4,1,'assistant','I\'m doing well, thank you for asking!  As a large language model, I don\'t experience emotions or feelings in the same way humans do, but I\'m functioning optimally and ready to assist you. How can I help you today?\n','null',NULL,'2025-09-25 19:36:40'),(5,2,'user','hello',NULL,NULL,'2025-09-26 10:02:42'),(6,2,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:02:43'),(7,2,'user','hello',NULL,NULL,'2025-09-26 10:04:54'),(8,2,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:04:55'),(9,3,'user','hrllo',NULL,NULL,'2025-09-26 10:07:35'),(10,3,'assistant','❌ Sorry, I encountered an error while generating the response: 404 Publisher Model `projects/generativelanguage-ga/locations/us-central1/publishers/google/models/gemini-1.5-flash-002` was not found or your project does not have access to it. Please ensure you are using a valid model version. For more information, see: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions','null',NULL,'2025-09-26 10:07:36'),(11,3,'user','hello',NULL,NULL,'2025-09-26 10:07:51'),(12,3,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:07:52'),(13,4,'user','hello',NULL,NULL,'2025-09-26 10:13:06'),(14,4,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:13:08'),(15,5,'user','hello',NULL,NULL,'2025-09-26 10:15:56'),(16,5,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:15:57'),(17,6,'user','hello',NULL,NULL,'2025-09-26 10:16:21'),(18,6,'assistant','❌ Sorry, I encountered an error while generating the response: 404 Publisher Model `projects/generativelanguage-ga/locations/us-central1/publishers/google/models/gemini-1.5-flash-002` was not found or your project does not have access to it. Please ensure you are using a valid model version. For more information, see: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions','null',NULL,'2025-09-26 10:16:22'),(19,7,'user','hi',NULL,NULL,'2025-09-26 10:16:59'),(20,7,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:16:59'),(21,8,'user','hello',NULL,NULL,'2025-09-26 10:25:34'),(22,8,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:25:36'),(23,9,'user','hello',NULL,NULL,'2025-09-26 10:28:44'),(24,9,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:28:45'),(25,10,'user','hello',NULL,NULL,'2025-09-26 10:30:56'),(26,10,'assistant','❌ Gemini API not configured. Please set GEMINI_API_KEY.','null',NULL,'2025-09-26 10:30:56'),(27,11,'user','hello',NULL,NULL,'2025-09-26 10:38:40'),(28,11,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:38:41'),(29,11,'user','hello',NULL,NULL,'2025-09-26 10:38:49'),(30,11,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 10:38:50'),(31,12,'user','hello',NULL,NULL,'2025-09-26 10:40:50'),(32,12,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:40:51'),(33,13,'user','hello',NULL,NULL,'2025-09-26 10:43:23'),(34,13,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:43:24'),(35,14,'user','hello',NULL,NULL,'2025-09-26 10:43:43'),(36,14,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:43:44'),(37,15,'user','hello',NULL,NULL,'2025-09-26 10:46:17'),(38,15,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:46:18'),(39,15,'user','Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format   still getting same error',NULL,NULL,'2025-09-26 10:46:38'),(40,15,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:46:39'),(41,16,'user','hello',NULL,NULL,'2025-09-26 10:48:13'),(42,16,'assistant','❌ Sorry, I encountered an error while generating the response: 400 * GenerateContentRequest.model: unexpected model name format\n','null',NULL,'2025-09-26 10:48:14'),(43,17,'user','hello',NULL,NULL,'2025-09-26 10:53:07'),(44,17,'assistant','❌ Sorry, I encountered an error while generating the response: 404 Publisher Model `projects/generativelanguage-ga/locations/us-central1/publishers/google/models/gemini-1.5-flash-002` was not found or your project does not have access to it. Please ensure you are using a valid model version. For more information, see: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions','null',NULL,'2025-09-26 10:53:09'),(45,18,'user','hello',NULL,NULL,'2025-09-26 10:57:47'),(46,18,'assistant','❌ Sorry, I encountered an error while generating the response: 404 Publisher Model `projects/generativelanguage-ga/locations/us-central1/publishers/google/models/gemini-1.5-flash-002` was not found or your project does not have access to it. Please ensure you are using a valid model version. For more information, see: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions','null',NULL,'2025-09-26 10:57:50'),(47,19,'user','hello',NULL,NULL,'2025-09-26 11:03:16'),(48,19,'assistant','Hello! My apologies, but I cannot answer that question based on the provided documents. The documents contain information related to SQL commands, database concepts, and multiple-choice questions about databases.','\"[{\\\"filename\\\": \\\"1000 CCEE MCQ DATABASE.pdf\\\", \\\"document_id\\\": 2, \\\"similarity_score\\\": 0.373, \\\"preview\\\": \\\"a) . \\\\nb) \\\\u2013 \\\\nc) : \\\\nd) , \\\\nView  Answer  \\\\n \\\\nAnswer:  b \\\\nExplanation:  \\\\nEXEC SQL \\\\nDECLARE c cursor FOR \\\\nSELECT ID, name  \\\\nFROM student \\\\nWHERE tot cred > :credit amount; \\\\n \\\\n. \\\\n \\\\nd) EXEC  SQL  update  END -\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.371, \\\"preview\\\": \\\"139. The SQL statement \\\\\\\"DELETE FROM orders WHERE order_status = \'cancelled\';\\\\\\\" will:  \\\\na) Insert new orders wi th the status \'cancelled\'  \\\\nb) Update the status of all orders to \'cancelled\'  \\\\nc) Delete \\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.369, \\\"preview\\\": \\\"76. The SQL statement \\\\\\\"SELECT * FROM customers;\\\\\\\" retrieves:  \\\\na) All records from the \\\\\\\"customers\\\\\\\" table  \\\\nb) All columns from the \\\\\\\"customers\\\\\\\" table  \\\\nc) All rows and columns from the database  \\\\nd) All\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.369, \\\"preview\\\": \\\": \\\\na) Insert a new customer record with ID 101  \\\\nb) Update the customer record with ID 101  \\\\nc) Delete the customer record with ID 101  \\\\nd) Retrieve the customer record with ID 101  \\\\n \\\\nAnswer: c) Dele\\\"}, {\\\"filename\\\": \\\"SQL Notes 101pages.pdf\\\", \\\"document_id\\\": 5, \\\"similarity_score\\\": 0.368, \\\"preview\\\": \\\"OrderId ProductName OrderDate\\\\n1 Geitost 2008-11-11\\\\n3 Mozzarella di Giovanni 2008-11-11\\\\nNow, assume that the \\\\\\\"Orders\\\\\\\" table looks like this (notice the time component in the \\\\\\\"OrderDate\\\\\\\"\\\\ncolumn):\\\\nOrderI\\\"}]\"',0.371272,'2025-09-26 11:03:20'),(49,19,'user','hello',NULL,NULL,'2025-09-26 11:03:25'),(50,19,'assistant','Sorry, I couldn\'t generate a response at the moment.','null',NULL,'2025-09-26 11:03:25'),(51,20,'user','hello',NULL,NULL,'2025-09-26 11:13:16'),(52,20,'assistant','Hello! I am an AI assistant designed to answer questions based on the provided context from your documents. How can I help you today?','\"[{\\\"filename\\\": \\\"1000 CCEE MCQ DATABASE.pdf\\\", \\\"document_id\\\": 2, \\\"similarity_score\\\": 0.373, \\\"preview\\\": \\\"a) . \\\\nb) \\\\u2013 \\\\nc) : \\\\nd) , \\\\nView  Answer  \\\\n \\\\nAnswer:  b \\\\nExplanation:  \\\\nEXEC SQL \\\\nDECLARE c cursor FOR \\\\nSELECT ID, name  \\\\nFROM student \\\\nWHERE tot cred > :credit amount; \\\\n \\\\n. \\\\n \\\\nd) EXEC  SQL  update  END -\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.371, \\\"preview\\\": \\\"139. The SQL statement \\\\\\\"DELETE FROM orders WHERE order_status = \'cancelled\';\\\\\\\" will:  \\\\na) Insert new orders wi th the status \'cancelled\'  \\\\nb) Update the status of all orders to \'cancelled\'  \\\\nc) Delete \\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.369, \\\"preview\\\": \\\"76. The SQL statement \\\\\\\"SELECT * FROM customers;\\\\\\\" retrieves:  \\\\na) All records from the \\\\\\\"customers\\\\\\\" table  \\\\nb) All columns from the \\\\\\\"customers\\\\\\\" table  \\\\nc) All rows and columns from the database  \\\\nd) All\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.369, \\\"preview\\\": \\\": \\\\na) Insert a new customer record with ID 101  \\\\nb) Update the customer record with ID 101  \\\\nc) Delete the customer record with ID 101  \\\\nd) Retrieve the customer record with ID 101  \\\\n \\\\nAnswer: c) Dele\\\"}, {\\\"filename\\\": \\\"SQL Notes 101pages.pdf\\\", \\\"document_id\\\": 5, \\\"similarity_score\\\": 0.368, \\\"preview\\\": \\\"OrderId ProductName OrderDate\\\\n1 Geitost 2008-11-11\\\\n3 Mozzarella di Giovanni 2008-11-11\\\\nNow, assume that the \\\\\\\"Orders\\\\\\\" table looks like this (notice the time component in the \\\\\\\"OrderDate\\\\\\\"\\\\ncolumn):\\\\nOrderI\\\"}]\"',0.371272,'2025-09-26 11:13:18'),(53,20,'user','hello',NULL,NULL,'2025-09-26 11:13:27'),(54,20,'assistant','Hello! How can I help you today?','null',NULL,'2025-09-26 11:13:28'),(55,20,'user','I am good tell me something abouut you',NULL,NULL,'2025-09-26 11:13:42'),(56,20,'assistant','That\'s good to hear! I\'m doing well, operating as intended.\n\nAs for me, I\'m a large language model, an AI developed by Google.\n\nHere\'s a bit about me:\n\n*   **What I am:** I\'m a computer program designed to understand and generate human-like text. I don\'t have a physical body, consciousness, personal feelings, or experiences like humans do.\n*   **What I do:** My primary function is to process information, answer questions, generate creative content, summarize texts, translate languages, write code, and assist users with a wide range of tasks based on the vast amount of data I was trained on.\n*   **My \"goal\":** My purpose is to be helpful, informative, and to make complex information more accessible.\n\nSo, while I can\'t tell you about my weekend plans or what my favorite color is (because I don\'t have those!), my \"life\" revolves around processing information and interacting with users like you.\n\nWhat can I help you with today?','null',NULL,'2025-09-26 11:13:50'),(57,20,'user','top  5 sql queries',NULL,NULL,'2025-09-26 11:14:03'),(58,20,'assistant','Based on the provided context, here are five SQL queries:\n\n1.  `SELECT emp_name FROM department WHERE dept_name LIKE ’ Computer Science’` (Source: 1000 CCEE MCQ DATABASE.pdf)\n2.  `SELECT product_name, price FROM products ORDER BY price DESC;` (Source: DBMS Database 670 mcq.pdf)\n3.  `SELECT * FROM orders WHERE order_date BETWEEN \'2022 -01-01\' AND \'2022 -12-31\';` (Source: DBMS Database 670 mcq.pdf)\n4.  `SELECT * FROM products WHERE product_name LIKE \'App%\';` (Source: DBMS Database 670 mcq.pdf)\n5.  `SELECT DISTINCT department FROM employees;` (Source: DBMS Database 670 mcq.pdf)','\"[{\\\"filename\\\": \\\"1000 CCEE MCQ DATABASE.pdf\\\", \\\"document_id\\\": 2, \\\"similarity_score\\\": 0.51, \\\"preview\\\": \\\"a) Atleast,  Exactly  \\\\nb) Exactly,  Atleast  \\\\n \\\\n c) Atleast,  All \\\\nd) All, Exactly  \\\\nView  Answer  \\\\nAnswer:  b \\\\nExplanation:  None.  \\\\n \\\\n3. \\\\n \\\\nSELECT emp_name \\\\nFROM department  \\\\nWHERE dept_name  LIKE \\\\u2019\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.506, \\\"preview\\\": \\\"b) The total number of employees in each department  \\\\nc) A list of unique department names  \\\\nd) The average salary of employees in each department  \\\\n \\\\nAnswer: c) A list of unique department names  \\\\n \\\\n\\\"}, {\\\"filename\\\": \\\"DBMS Database 670 mcq.pdf\\\", \\\"document_id\\\": 3, \\\"similarity_score\\\": 0.501, \\\"preview\\\": \\\"183. The ORDER BY clause in SQL is used to:  \\\\na) Filter data based on a condition  \\\\nb) Retrieve data that matches a specific pattern  \\\\nc) Sort data in ascendi ng or descending order  \\\\nd) Join two or m\\\"}, {\\\"filename\\\": \\\"1000 CCEE MCQ DATABASE.pdf\\\", \\\"document_id\\\": 2, \\\"similarity_score\\\": 0.494, \\\"preview\\\": \\\"Database  Questions  and Answers  \\\\u2013 SQL  Queries  \\\\n \\\\nWhich  of these  query  will display  the the table given  above  ? \\\\na) Select  employee  from  name  \\\\nb) Select  name  \\\\nc) Select  name  from  emp\\\"}, {\\\"filename\\\": \\\"1000 CCEE MCQ DATABASE.pdf\\\", \\\"document_id\\\": 2, \\\"similarity_score\\\": 0.487, \\\"preview\\\": \\\"2. Ranking  of queries  is done  by which  of the following?  \\\\na) Group  by \\\\nb) Order  by \\\\nc) Having  \\\\nd) Both  Group  by and Order  by \\\\nView  Answer  \\\\nAnswer:  b \\\\nExplanation:  Order  by clause  arra\\\"}]\"',0.505442,'2025-09-26 11:14:08');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'vraj1091','vraj10@gmail.com','$2b$12$G82ubdfm1rZySVlV5L152OrUHWZtr9mQYlR8S1ZU27453CYAqW4RG',1,'2025-09-25 19:33:39',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vector_collections`
--

DROP TABLE IF EXISTS `vector_collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vector_collections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `collection_name` varchar(100) NOT NULL,
  `document_count` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_vector_collections_user_id` (`user_id`),
  KEY `ix_vector_collections_id` (`id`),
  CONSTRAINT `vector_collections_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vector_collections`
--

LOCK TABLES `vector_collections` WRITE;
/*!40000 ALTER TABLE `vector_collections` DISABLE KEYS */;
/*!40000 ALTER TABLE `vector_collections` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-26 11:24:43
