package com.computerwhz.command;

import com.computerwhz.Command;
import com.computerwhz.Main;

public class BackupAllCommand implements Command {
    @Override
    public void execute(String[] args) {
        Main.getBackupManager().BackUpAll();
    }
}
