create database TFM;
use TFM;

CREATE TABLE `USUARIO` (
	`ID` INT NOT NULL AUTO_INCREMENT,
	`Nombre` VARCHAR(50) NOT NULL,
	`Usuario` VARCHAR(50) NOT NULL,
	`Password` VARCHAR(50) NOT NULL,
	`Correo` VARCHAR(50) NOT NULL,
	PRIMARY KEY (`ID`)
)
COLLATE='utf8mb4_general_ci';

REATE TABLE `CANCION` (
	`id` INT NOT NULL,
	`Titulo` VARCHAR(50) NULL DEFAULT NULL,
	`Fecha` DATE NULL DEFAULT NULL,
	`Procesado` CHAR(50) NULL DEFAULT NULL,
	`Estilo` VARCHAR(50) NULL DEFAULT NULL,
	`Usuario` INT NULL,
	PRIMARY KEY (`id`),
	INDEX `Usuario` (`Usuario`),
	CONSTRAINT `FKUSU` FOREIGN KEY (`Usuario`) REFERENCES `usuario` (`ID`)
)
COLLATE='utf8mb4_general_ci';

CREATE TABLE `FICHERO` (
	`ID` INT NOT NULL,
	`TITULO` VARCHAR(50) NULL DEFAULT NULL,
	`RUTA` VARCHAR(50) NULL DEFAULT NULL,
	`CANCION` INT NULL,
	PRIMARY KEY (`ID`),
	INDEX `CANCION` (`CANCION`),
	CONSTRAINT `FKCAN` FOREIGN KEY (`CANCION`) REFERENCES `cancion` (`id`)
)
COLLATE='utf8mb4_general_ci';
