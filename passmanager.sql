-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Počítač: 127.0.0.1
-- Vytvořeno: Ned 06. dub 2025, 14:51
-- Verze serveru: 10.4.32-MariaDB
-- Verze PHP: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Databáze: `python`
--

-- --------------------------------------------------------

--
-- Struktura tabulky `masterpass`
--

CREATE TABLE `masterpass` (
  `salt` varchar(512) DEFAULT NULL,
  `setup` tinyint(4) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Vypisuji data pro tabulku `masterpass`
--

INSERT INTO `masterpass` (`salt`, `setup`) VALUES
('blMH4YtqKdNLbuL5h1zX2Q==', 1);

-- --------------------------------------------------------

--
-- Struktura tabulky `passmanager`
--

CREATE TABLE `passmanager` (
  `id` int(11) NOT NULL,
  `url` varchar(2048) NOT NULL,
  `username` varchar(1000) NOT NULL,
  `password` varchar(512) NOT NULL,
  `note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Vypisuji data pro tabulku `passmanager`
--

INSERT INTO `passmanager` (`id`, `url`, `username`, `password`, `note`) VALUES
(7, 'https://example.com', 'test', 'Djo+oir+', '');

--
-- Indexy pro exportované tabulky
--

--
-- Indexy pro tabulku `passmanager`
--
ALTER TABLE `passmanager`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pro tabulky
--

--
-- AUTO_INCREMENT pro tabulku `passmanager`
--
ALTER TABLE `passmanager`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
