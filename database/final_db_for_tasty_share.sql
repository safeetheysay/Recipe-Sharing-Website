-- phpMyAdmin SQL Dump
-- version 3.4.5
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 01, 2026 at 05:20 PM
-- Server version: 5.5.16
-- PHP Version: 5.3.8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `python assignment`
--

-- --------------------------------------------------------

--
-- Table structure for table `comments`
--

CREATE TABLE IF NOT EXISTS `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `comment_text` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=82 ;

--
-- Dumping data for table `comments`
--

INSERT INTO `comments` (`id`, `recipe_id`, `user_id`, `comment_text`, `created_at`) VALUES
(22, 16, 25, 'perfectooooooooo', '2025-10-22 22:26:17'),
(52, 24, 25, 'asdas', '2025-10-24 10:54:04'),
(53, 24, 25, 'asdasdas', '2025-10-24 10:54:14'),
(54, 24, 25, 'asdasda', '2025-10-24 10:54:19'),
(55, 24, 25, 'asdasqweqw', '2025-10-24 10:54:21'),
(56, 22, 37, 'asdasdasdas', '2025-10-24 10:56:32'),
(57, 22, 37, 'hey buddy ', '2025-10-24 11:28:25'),
(58, 24, 37, 'asdasdas', '2025-10-24 11:28:36'),
(59, 24, 29, 'hey this thing is so good', '2025-10-24 11:33:39'),
(60, 24, 29, 'yeah perfectly fine trhis is totally awesome', '2025-10-24 11:34:08'),
(63, 20, 37, 'yeahhhhhhhh', '2025-10-24 11:40:57'),
(65, 20, 37, 'nigaa what', '2025-10-24 11:52:10'),
(72, 25, 37, 'asdas', '2025-10-24 21:33:20'),
(74, 20, 37, 'asdasdas', '2025-10-24 22:05:47'),
(75, 19, 29, 'hello 3 this recipe is so good', '2025-10-24 23:31:52'),
(77, 25, 29, 'hehhe', '2025-10-24 23:33:57'),
(78, 25, 29, 'kasdhjkadjkdhad', '2025-10-25 14:54:19'),
(80, 25, 25, 'dsa', '2025-10-26 11:32:07'),
(81, 29, 40, 'ahsja\n', '2025-10-26 18:42:09');

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE IF NOT EXISTS `favorites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `recipe_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recipe_title` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_favorite` (`user_id`,`recipe_id`),
  KEY `recipe_id` (`recipe_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=90 ;

--
-- Dumping data for table `favorites`
--

INSERT INTO `favorites` (`id`, `user_id`, `recipe_id`, `created_at`, `recipe_title`) VALUES
(82, 37, 18, '2025-10-24 22:06:21', 'asdas'),
(84, 25, 25, '2025-10-26 09:19:43', 'qweqwe'),
(85, 25, 20, '2025-10-26 09:19:45', 'curry'),
(87, 40, 29, '2025-10-26 18:41:16', '123'),
(89, 22, 31, '2025-10-26 20:56:27', 'as');

-- --------------------------------------------------------

--
-- Table structure for table `feedbacks`
--

CREATE TABLE IF NOT EXISTS `feedbacks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `feedbacks`
--

INSERT INTO `feedbacks` (`id`, `user_id`, `email`, `message`, `created_at`) VALUES
(4, 25, '3@gmail.com', 'Hello admin How r u?', '2025-09-25 19:19:55'),
(6, 37, 'newer@gmail.com', 'hello\r\n', '2025-10-19 16:24:48'),
(7, 25, '3s@gmail.com', 'your shop is very good', '2025-10-26 09:29:41'),
(8, 40, 'safeerahmadawan68208@gmail.com', 'uit697y\r\n', '2025-10-26 18:42:51');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `recipe_id` int(11) DEFAULT NULL,
  `comment_id` int(11) DEFAULT NULL,
  `commenter_id` int(11) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `comment_id` (`comment_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=34 ;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `recipe_id`, `comment_id`, `commenter_id`, `message`, `is_read`, `created_at`) VALUES
(29, 22, NULL, NULL, 22, 'Password Reminder: It''s been 15 days since your last password change. Consider updating your password for security.', 0, '2025-11-12 04:48:48'),
(30, 25, NULL, NULL, 25, 'Password Reminder: It''s been 15 days since your last password change. Consider updating your password for security.', 0, '2025-11-12 04:48:48'),
(31, 29, NULL, NULL, 29, 'Password Reminder: It''s been 15 days since your last password change. Consider updating your password for security.', 0, '2025-11-12 04:48:48'),
(32, 37, NULL, NULL, 37, 'Password Reminder: It''s been 15 days since your last password change. Consider updating your password for security.', 0, '2025-11-12 04:48:48'),
(33, 40, NULL, NULL, 40, 'Password Reminder: It''s been 15 days since your last password change. Consider updating your password for security.', 0, '2025-11-12 04:48:48');

-- --------------------------------------------------------

--
-- Table structure for table `recipes`
--

CREATE TABLE IF NOT EXISTS `recipes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `ingredients` text NOT NULL,
  `steps` text NOT NULL,
  `category` varchar(100) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=37 ;

--
-- Dumping data for table `recipes`
--

INSERT INTO `recipes` (`id`, `title`, `ingredients`, `steps`, `category`, `image_path`, `user_id`, `status`, `created_at`) VALUES
(16, 'Biryani', 'asjd', 'asdjkl', 'askdjlak', 'uploads/recipes/3_20250921_200127_biryani.jpeg', 3, 'approved', '2025-09-21 15:01:27'),
(17, 'Dish', 'sdjas', 'asdas', 'asdas', 'uploads/recipes/22_20250921_221214_biryani.jpeg', 22, 'approved', '2025-09-21 17:12:14'),
(18, 'asdas', 'asdas', 'asdasd', 'asdas', 'uploads/recipes/3_20250921_221503_images.jpeg', 3, 'approved', '2025-09-21 17:15:04'),
(19, 'Chicken Curry', 'chicken', '15', 'Drinks', 'uploads/recipes/25_20250922_034502_download.jpeg', 25, 'approved', '2025-09-21 22:45:03'),
(20, 'curry', 'i dont know', '5 ', 'All Categories', 'uploads/recipes/29_20250926_001734_download.jpeg', 29, 'approved', '2025-09-25 19:17:34'),
(22, '11', '111', '111', 'All Categories', NULL, 37, 'approved', '2025-10-19 16:25:00'),
(24, 'asd', 'asd', 'asd', 'All Categories', NULL, 37, 'rejected', '2025-10-19 21:29:52'),
(25, 'qweqwe', 'asd', 'asd', 'All Categories', NULL, 37, 'approved', '2025-10-19 21:40:44'),
(28, 'testing final recipe addition', 'many', '123', 'Non-Vegeterian', NULL, 29, 'approved', '2025-10-25 15:30:12'),
(29, '123', '1234', '123', 'Vegeterian', NULL, 29, 'approved', '2025-10-25 15:36:21'),
(30, '123123', '123', '123', 'Vegeterian', NULL, 29, 'rejected', '2025-10-25 15:36:50'),
(31, 'as', 'as', 'as', 'Non-Vegeterian', NULL, 25, 'approved', '2025-10-26 11:38:18'),
(32, 'asd', 'asd', 'asd', 'Desserts', NULL, 25, 'approved', '2025-10-26 11:49:52'),
(33, 'asdasdasd', 'asasddasasd', 'asd', 'Drinks', NULL, 25, 'rejected', '2025-10-26 11:52:01'),
(35, 'daskjdklasjk', 'asdas', 'asdas', 'Vegeterian', 'uploads/recipes/25_20251026_201154_WhatsApp_Image_2025-09-26_at_10.30.55_ad7545e9.jpg', 25, 'rejected', '2025-10-26 15:11:54'),
(36, 'auiu', 'sjsdjhsodh', 'sjf sdhso sdjsipd sdhjiofd', 'Desserts', 'uploads/recipes/40_20251026_234451_IMG-20251024-WA0010.jpg', 40, 'rejected', '2025-10-26 18:44:51');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE IF NOT EXISTS `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text NOT NULL,
  `user_id` int(11) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=10 ;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `recipe_id`, `title`, `rating`, `comment`, `user_id`, `user_email`, `created_at`) VALUES
(1, 16, 'Biryani', 5, 'Great', 18, 'user@gmail.com', '2025-09-21 16:30:47'),
(3, 17, 'Dish', 3, 'great recipe', 3, 'new@gmail.com', '2025-09-21 17:15:41'),
(5, 16, 'Biryani', 4, 'good dish', 25, '3@gmail.com', '2025-09-25 19:19:40'),
(6, 20, 'curry', 2, 'nice', 25, '3s@gmail.com', '2025-10-26 14:51:04'),
(7, 17, 'Dish', 4, 'kkk', 22, 'safeer@gmail.com', '2025-10-26 15:18:18'),
(8, 33, 'asdasdasd', 5, 'asd', 22, 'safeer@gmail.com', '2025-10-26 15:28:10'),
(9, 29, '123', 4, 'yjhktuyjyj', 40, 'safeerahmadawan68208@gmail.com', '2025-10-26 18:42:34');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `cnic` varchar(20) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `picture` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'user',
  `password_last_changed` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=41 ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `phone`, `cnic`, `password`, `picture`, `role`, `password_last_changed`) VALUES
(3, '1', 'new@gmail.com', '12312312312', '123131231231231', '123', NULL, 'admin', '2025-10-27 00:26:41'),
(22, 'safeer', 'safeer@gmail.com', '123123123123', '123123123123123', '123', 'uploads/users/safeer_20251027_015454_WhatsApp_Image_2025-10-09_at_10.36.03_b34677c1.jpg', 'user', '2025-10-27 00:26:41'),
(25, '3', '3s@gmail.com', '12312312312312', '12312312312', '123', 'uploads/users/3_20251024_151058_Astronaut_BG.png', 'user', '2025-10-27 00:26:41'),
(29, 'Abeera ', 'abeerakhan@gmail.com', '0341476812367812', '1231231231', '123', 'uploads/users/Abeera _20251025_194925_WhatsApp_Image_2025-10-06_at_11.15.26_e3660158.jpg', 'user', '2025-10-12 01:43:31'),
(35, 'admin', 'adminnew@gmail.com', '123123', '12312312312', '123', 'uploads/users/admin_admin_20251025_041848_WhatsApp_Image_2025-10-14_at_10.16.53_0ff8a73c.jpg', 'admin', '2025-10-27 00:26:41'),
(37, 'safee awan', 'test@gmail.com', '1231231', '330134', '123', 'uploads/users/safee_20251025_023022_Ice_Cream.jpg', 'user', '2025-10-27 00:26:41'),
(40, 'urooj', 'safeerahmadawan68208@gmail.com', '03063964605', '345344434534', 'maham', 'uploads/users/urooj_20251026_233946_IMG-20251024-WA0009.jpg', 'user', '2025-10-27 00:26:41');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`),
  ADD CONSTRAINT `notifications_ibfk_3` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`);

--
-- Constraints for table `recipes`
--
ALTER TABLE `recipes`
  ADD CONSTRAINT `recipes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
