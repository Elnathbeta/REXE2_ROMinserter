#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
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
        self.LOGGER.debug("[{}] Inserting new bytes at {}".format(os.path.basename(file_obj.name), hex(self.Insert_offset)))
        self.ROM.write(file_obj.read())
        # RECHERCHE DE POINTEURS ET REMPLACEMENT




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
