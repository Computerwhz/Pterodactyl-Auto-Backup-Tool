package com.computerwhz.command;

import com.computerwhz.BackupTimer;
import com.computerwhz.Command;
import com.computerwhz.Main;

public class CancelTimerCommand implements Command {
    @Override
    public void execute(String[] strings) {
        if (Main.getTimer().isRunning()){
            Main.getTimer().stopTimer();
            System.out.println("Stopped Timer");
        }
        else {
            System.err.println("No timer is running");
        }
    }
}
