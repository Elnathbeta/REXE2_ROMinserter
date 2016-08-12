#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import io
import logmodule

ROM_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "ROM.bin")) # Le fichier de la ROM
NEW_FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "new_files")) # Dossier avec les fichiers à inserer
INSERT_AT = 0x21 # Où insérer les fichiers (normalement la fin de la ROM)
VIRTUAL_OFFSET = 0x80000000 # Offset "virtuel" rajouté à tous les pointeurs
POINTER_SIZE = 4 # Taille d'un pointeur en octets

LOGLEVEL = "debug"
LOGMODULE_OPTIONS = {
    "stdout_dateformat": "%H:%M:%S",
    "stderr_dateformat": "%H:%M:%S",
}

class Inserter():
    def __init__(self, rom, insert_at, virtual_offset, pointer_size, logger):
        """
            Initialise l'inserter.
            :param rom: Fichier ROM où on va insérer les textes.
            :type rom: file object (openend in binary mode)
            :param insert_at: Où insérer les fichiers (offset dans la ROM)
            :type insert_at: int
            :param virtual_offset: Offset "virtuel" rajouté à tous les pointeurs
            :type virtual_offset: int
            :param pointer_size: Taille d'un pointeur en octets
            :type pointer_size: int
            :logger: Logger utilisé pour logger toute l'activitée
            :type logger: logmodule.Logger
        """
        self.ROM = rom
        self.Insert_offset = insert_at
        self.VIRTUAL_OFFSET = virtual_offset
        self.POINTER_SIZE = pointer_size
        self.LOGGER = logger

    def insert(self, file_obj, old_address):
        """
            Ajoute un fichier à Insert_offset.
            :param file_obj: le fichier à ajouter
            :type file_obj: file object (open in binary mode)
            :param old_address: Tous les pointeurs pointant ici seront remplacés par des pointeurs pointant sur la nouvelle adresse. VIRTUAL_OFFSET sera ajouté à cette valeur.
            :type old_address: int
        """
        # INSERTION DU NOUVEAU FICHIER
        self.ROM.seek(self.Insert_offset)
        self.LOGGER.info("[{}] Inserting new bytes at {}".format(os.path.basename(file_obj.name), hex(self.Insert_offset)))
        self.ROM.write(file_obj.read())
        # CALCUL DES POINTEURS ET MISE À JOUR DE Insert_offset
        new_pointer = self.Insert_offset + self.VIRTUAL_OFFSET
        self.LOGGER.debug("[{}] Pointer to new text: {}".format(os.path.basename(file_obj.name), hex(new_pointer)))
        while self.ROM.tell() % 4: #Le texte suivant doit commencer forcément à un multiple de 4
            self.ROM.write(b'\x00')
        self.Insert_offset = self.ROM.tell()
        self.LOGGER.debug("[{}] Next text will start at {}".format(os.path.basename(file_obj.name), hex(self.Insert_offset)))
        # RECHERCHE DE POINTEURS ET REMPLACEMENT
        self.ROM.seek(0)
        byte_sequence = [ord(self.ROM.read(1)) for _ in range(self.POINTER_SIZE)] #On initialise en lisant les premiers octets qui pourraient composer un pointeur
        replacement_list = [] # Juste pour info, on affichera où on fait des remplacements
        while True:
            if self.little_endian_to_decimal(byte_sequence) == (old_address + self.VIRTUAL_OFFSET):
                self.LOGGER.debug("[{}] Old pointer found at {}".format(os.path.basename(file_obj.name), hex(self.ROM.tell() - self.POINTER_SIZE)))
                replacement_list.append(self.ROM.tell())
                self.ROM.seek(-self.POINTER_SIZE, io.SEEK_CUR)
                self.ROM.write(new_pointer.to_bytes(self.POINTER_SIZE, "little")) # On écrit les octets en little endian
            b = self.ROM.read(1)
            if b == b'':
                break
            byte_sequence.pop(0)
            byte_sequence.append(ord(b))
        self.LOGGER.info("[{}] {} pointers replaced. {}".format(os.path.basename(file_obj.name), len(replacement_list), ', '.join([hex(x) for x in replacement_list])))

    @staticmethod
    def decimal_to_little_endian(n):
        """
            Conversion d'un nombre positif decimal en suite de valeurs en little endian.
            chaque element du resultat est la valeur d'un octet.
            :rtype: list of int
        """
        result = []
        while(n > 0):
            byte = n % 16
            n = n // 16
            byte += (n % 16) * 16
            n = n // 16
            result.append(byte)
        return result

    @staticmethod
    def little_endian_to_decimal(bytelist):
        """
            Interpretation d'une suite de valeurs en tant qu'un seul nombre codé en little endian.
            Les valeurs sont interpretés avec int(valeur, 0): "0x10", "16", 16 ont la même valeur.
            :rtype: int
        """
        result = 0
        for power, value in enumerate(bytelist):
            result += int(str(value), 0) * 256**power
        return result


if __name__ == '__main__':
    MainLogger = logmodule.Logger(__name__, LOGLEVEL, logmodule.HANDLER_ALL, **LOGMODULE_OPTIONS)
    MainLogger.info("===== Program start =====")
    if not os.path.isfile(ROM_FILENAME):
        MainLogger.critical("Rom file not found! Exiting.")
        sys.exit(1)
    with open(ROM_FILENAME, "r+b") as rom:
        inserter = Inserter(rom, INSERT_AT, VIRTUAL_OFFSET, POINTER_SIZE, MainLogger)
        for entry in os.listdir(NEW_FILES_DIR):
            filepath = os.path.join(NEW_FILES_DIR, entry)
            if os.path.isfile(filepath):
                MainLogger.info("Starting insert of {}".format(entry))
                old_address = int(os.path.splitext(entry)[0], 16) #On interprete le nom comme une adresse hexa
                with open(filepath, "rb") as f:
                    inserter.insert(f, old_address)
                MainLogger.info("{} inserted".format(entry))
    MainLogger.info("All files inserted.")
