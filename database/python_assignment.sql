-- phpMyAdmin SQL Dump
-- version 3.4.5
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Sep 21, 2025 at 07:44 PM
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
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `feedbacks`
--

INSERT INTO `feedbacks` (`id`, `user_id`, `email`, `message`, `created_at`) VALUES
(1, 20, 'insan@gmail.com', 'aksdjakld', '2025-09-21 18:57:42'),
(2, 20, 'insan@gmail.com', 'Good', '2025-09-21 18:58:08'),
(3, 20, 'insan@gmail.com', 'All is Good ADmin', '2025-09-21 19:34:33');

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
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=19 ;

--
-- Dumping data for table `recipes`
--

INSERT INTO `recipes` (`id`, `title`, `ingredients`, `steps`, `category`, `image_path`, `user_id`, `status`, `created_at`) VALUES
(16, 'Biryani', 'asjd', 'asdjkl', 'askdjlak', 'uploads/recipes/3_20250921_200127_biryani.jpeg', 3, 'approved', '2025-09-21 15:01:27'),
(17, 'Dish', 'sdjas', 'asdas', 'asdas', 'uploads/recipes/22_20250921_221214_biryani.jpeg', 22, 'approved', '2025-09-21 17:12:14'),
(18, 'asdas', 'asdas', 'asdasd', 'asdas', 'uploads/recipes/3_20250921_221503_images.jpeg', 3, 'approved', '2025-09-21 17:15:04');

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
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `recipe_id`, `title`, `rating`, `comment`, `user_id`, `user_email`, `created_at`) VALUES
(1, 16, 'Biryani', 5, 'Great', 18, 'user@gmail.com', '2025-09-21 16:30:47'),
(2, 16, 'Biryani', 4, 'asd', 20, 'insan@gmail.com', '2025-09-21 16:50:36'),
(3, 17, 'Dish', 3, 'great recipe', 3, 'new@gmail.com', '2025-09-21 17:15:41');

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
  `password` varchar(100) NOT NULL,
  `picture` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=27 ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `phone`, `cnic`, `password`, `picture`, `role`) VALUES
(3, 'admin', 'new@gmail.com', '12312312312', '123131231231231', '123', NULL, 'admin'),
(18, 'user', 'user@gmail.com', '12312312312', '12312312312', '123', NULL, 'user'),
(20, 'Insan', 'insan@gmail.com', '12312312312', '3123123123123', '123', NULL, 'user'),
(21, 'asf', 'qweq@gmail.com', 'qweqw', 'asd', 'qw', NULL, 'user'),
(22, 'safeer', 'safeer@gmail.com', '123123123123', '123123123123123', '123', NULL, 'user'),
(23, 'niggaman', 'niggaman@gmail.com', '123123123', '1231231231', '123', NULL, 'user'),
(24, 'niggaman2', 'nig@gmail.com', '123123123', '1231231231', '123', NULL, 'user'),
(25, '3', '3@gmail.com', '123123123', '12313131', '123', NULL, 'user'),
(26, '213', 'ad@g.com', '131', '1231231', '111', 'uploads/users/213_20250922_001233_download.jpeg', 'user');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recipes`
--
ALTER TABLE `recipes`
  ADD CONSTRAINT `recipes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
