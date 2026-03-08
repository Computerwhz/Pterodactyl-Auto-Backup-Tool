package com.computerwhz;

import com.mattmalec.pterodactyl4j.client.entities.ClientServer;

import java.util.Timer;
import java.util.TimerTask;

public class BackupTimer {

    private boolean isRunning;
    private Timer timer;

    public void runTimer(long time, boolean repeat, ClientServer server) {
        if (isRunning) {
            System.err.println("Could not run timer because it is already running");
            return;
        }

        TimerTask timerTask = new TimerTask() {
            @Override
            public void run() {
                if (server == null) {
                    Main.getBackupManager().BackUpAll();
                }
                else {
                    Main.getBackupManager().BackUp(server);
                }
                timer.cancel();
                timer = null;
                isRunning = false;
                if (repeat){
                    runTimer(time, repeat, server);
                }
            }
        };
        timer = new Timer();
        timer.schedule(timerTask, time);
        isRunning = true;
    }

    public void stopTimer() {
        timer.cancel();
        timer = null;
        isRunning = false;
    }

    public boolean isRunning() { return isRunning; }

}
