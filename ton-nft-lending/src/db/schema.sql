DROP TABLE IF EXISTS `nfts`;
DROP TABLE IF EXISTS `history`;
DROP TABLE IF EXISTS `configs`;

CREATE TABLE `nfts` (
  `id` integer,
  `address` varchar(255),
  `name` varchar(255),
  `owner_id` integer,
  `owner_address` varchar(255),
  `received_at` integer,
  `status` varchar(255),
  PRIMARY KEY (`id` AUTOINCREMENT)
);

CREATE TABLE `history` (
  `id` integer,
  `borrower_id` integer,
  `borrower_address` varchar(255),
  `nft_id` integer,
  `occurred_at` integer,
  PRIMARY KEY (`id` AUTOINCREMENT),
  FOREIGN KEY (`nft_id`) REFERENCES `nfts` (`id`)
);

CREATE TABLE `configs` (
  `id` integer,
  `timestamp` integer,
  `borrow_cost_per_second` integer,
  `lend_income_per_second` integer,
  `takeback_fee_per_request` integer,
  `borrow_duration_in_second` integer,
  PRIMARY KEY (`id` AUTOINCREMENT)
);

INSERT INTO `configs` (`timestamp`, `borrow_cost_per_second`, `lend_income_per_second`, `takeback_fee_per_request`, `borrow_duration_in_second`) VALUES (0, 20000000, 10000000, 1000000000, 60);


